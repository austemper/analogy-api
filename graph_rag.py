# =========================
# Imports / 初期化
# =========================

import os
import re
import ast
import json
import numpy as np
from google import genai

# =========================
# 定義
# =========================

NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+ssc://cb753f8e.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "cb753f8e")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

_embedder = None
_driver = None

def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _embedder

def get_driver():
    global _driver
    if _driver is None:
        from neo4j import GraphDatabase
        _driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    return _driver

EDGE_LABELS = {
    "HAS_MODE": "モードを持つ",
    "INSTANCE_OF": "構造に属する"
}

DOMAIN_COLOR_MAP = {
    "physical": "#4A90E2",      # blue
    "chemical": "#50E3C2",      # cyan
    "biological": "#7ED321",    # green
    "neural": "#BD10E0",        # purple
    "cognitive": "#9013FE",     # violet
    "social": "#F5A623",        # orange
    "formal": "#B8E986",        # light green
    "informational": "#417505", # dark green
    "philosophical": "#8B572A"  # brown
}

MODE_TYPE_MAP = {
    "flow": "流れ",
    "control": "制御",
    "optimization": "最適化",
    "emergence": "創発",
    "computation": "計算",
    "structure": "構造"
}

LLM_CALL_COUNT = 0
normalize_cache = {}
structure_cache = {}  # (name, level) → result
structure_cache = {}  # (name, level) → result
upper_cache = {}

# =========================
# ログ関数
# =========================

def log_step(step):
    print(f"\r[RUNNING] {step}", end="", flush=True)

# =========================
# LLM Call Counter
# =========================

def estimate_tokens(text):
    if not text:
        return 0
    # 日本語混在 → ざっくり 1token ≒ 2〜4文字
    return int(len(text) / 3)

def call_llm(prompt, tag="unknown"):
    global LLM_STATS

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    response_text = response.text if response.text else ""

    # --- トークン推定 ---
    prompt_tokens = estimate_tokens(prompt)
    response_tokens = estimate_tokens(response_text)

    # --- 統計更新 ---
    if tag not in LLM_STATS:
        LLM_STATS[tag] = {
            "calls": 0,
            "prompt_tokens": 0,
            "response_tokens": 0
        }

    LLM_STATS[tag]["calls"] += 1
    LLM_STATS[tag]["prompt_tokens"] += prompt_tokens
    LLM_STATS[tag]["response_tokens"] += response_tokens

    return response

# =========================
# LLM generate_modes
# =========================

def parse_llm_json(text):

    if text is None:
        return None

    text = text.strip()

    # markdown除去
    text = text.replace("```json", "").replace("```", "")

    # JSON部分抽出
    match = re.search(r'\{.*\}', text, re.DOTALL)

    if not match:
        print("JSONが見つかりません")
        print(text)
        return None

    json_text = match.group(0)

    try:
        return json.loads(json_text)

    except Exception as e:

        print("JSONのパース時にエラー発生:", e)
        print(json_text)

        return None

def generate_modes(concept):


    prompt = f"""
このコンセプトを動的振る舞いアナロジーとして分解せよ。

コンセプト:
{concept}

以下の6観点で必ず分解：

1. 流れ（flow）
2. 制御（control）
3. 最適化（optimization）
4. emergence（創発）
5. computation（計算）
6. structure（静的構造）

各々について以下を必ず明示：

- state（状態：蓄積量と駆動因子）
- transformation（変換：関数関係・方向）
- constraint（制約：保存則・安定条件・境界条件）
- dynamics（動的法則：時間発展）
- feedback（フィードバック特性）
- failure（破綻モード）
- structure（中間構造：抽象的ダイナミクス名）
重要：
structureは以下を満たせ：

・1〜2語の英語（snake_case）
・分野非依存の一般的パターン
・具体化禁止（例：packet_routingは禁止、routingは可）
・既存の概念のみ（新語禁止）
・各modeにつき1つのみ

出力は必ずJSON：

{{
  "modes": [
    {{
      "type": "flow",
      "state": "",
      "transformation": "",
      "constraint": "",
      "dynamics": "",
      "feedback": "",
      "failure": "",
      "structure": ""
    }},
    {{
      "type": "control",
      "state": "",
      "transformation": "",
      "constraint": "",
      "dynamics": "",
      "feedback": "",
      "failure": "",
      "structure": ""
    }},
    {{
      "type": "optimization",
      "state": "",
      "transformation": "",
      "constraint": "",
      "dynamics": "",
      "feedback": "",
      "failure": "",
      "structure": ""
    }},
    {{
      "type": "emergence",
      "state": "",
      "transformation": "",
      "constraint": "",
      "dynamics": "",
      "feedback": "",
      "failure": "",
      "structure": ""
    }},
    {{
      "type": "computation",
      "state": "",
      "transformation": "",
      "constraint": "",
      "dynamics": "",
      "feedback": "",
      "failure": "",
      "structure": ""
    }},
    {{
      "type": "structure",
      "state": "",
      "transformation": "",
      "constraint": "",
      "dynamics": "",
      "feedback": "",
      "failure": "",
      "structure": ""
    }},
  ]
}}

必ず3つすべて埋めること。
説明は簡潔に。
"""

    res = call_llm(prompt, tag="generate_modes")

    try:
        data = parse_llm_json(res.text)
        return data
    except Exception as e:
        print("Mode生成エラー:", e)
        print(res.text)
        return None   

# =========================
# LLM generate_concept_property
# =========================

def generate_description(concept):

    prompt = f"""
次の概念を本質的に定義し、ドメイン分類せよ。

概念:
{concept}

条件：

【説明】
・1文
・抽象的かつ本質的
・冗長禁止

【ドメイン】
以下から1つ選択：

physical
chemical
biological
neural
cognitive
social
formal
informational
philosophical

出力は必ずJSON：

{{
  "description": "",
  "domain": ""
}}
"""

    res = call_llm(prompt, tag="description_with_domain")

    data = parse_llm_json(res.text)

    if not data:
        return {
            "description": concept,
            "domain": "informational"
        }

    return data

# =========================
# LLM generate_upper_structure
# =========================

def generate_upper_structure(structure_key, level):

    prompt = f"""
次の構造の上位概念を生成せよ。

入力:
{structure_key}

条件：
・英語（snake_case）
・より一般的
・既存概念のみ

さらに：
・対応する日本語名も生成
・keyとname_jaは意味的に1対1対応させること

出力はJSON：

{{
  "key": "",
  "name_ja": ""
}}
"""

    res = call_llm(prompt, tag=f"upper_structure_L{level}")

    data = parse_llm_json(res.text)

    key = data["key"].strip().lower().replace(" ", "_")
    name_ja = data["name_ja"].strip()

    return key, name_ja


def build_structure_hierarchy(structure_key, structure_name_ja):

    # -------------------------
    # Level3
    # -------------------------
    s3_key, s3_name, s3_emb = resolve_structure(structure_name_ja, level=3)

    # -------------------------
    # Level2
    # -------------------------
    s2_raw = generate_upper_structure(s3_key, level=2)
    s2_key, s2_name, s2_emb = resolve_structure(s2_raw, level=2)

    # -------------------------
    # Level1
    # -------------------------
    s1_raw = generate_upper_structure(s2_key, level=1)
    s1_key, s1_name, s1_emb = resolve_structure(s1_raw, level=1)

    with get_driver().session() as session:

        # --- Level1 ---
        session.run("""
        MERGE (s:Structure {key:$key})
        SET s.level = 1,
            s.name_ja = $name,
            s.embedding = $emb
        """,
        key=s1_key,
        name=s1_name,
        emb=s1_emb.tolist()
        )

        # --- Level2 ---
        session.run("""
        MERGE (s:Structure {key:$key})
        SET s.level = 2,
            s.name_ja = $name,
            s.embedding = $emb
        """,
        key=s2_key,
        name=s2_name,
        emb=s2_emb.tolist()
        )

        # --- Level3 ---
        session.run("""
        MERGE (s:Structure {key:$key})
        SET s.level = 3,
            s.name_ja = $name,
            s.embedding = $emb
        """,
        key=s3_key,
        name=s3_name,
        emb=s3_emb.tolist()
        )

        # --- 関係 ---
        session.run("""
        MATCH (s3:Structure {key:$s3})
        MATCH (s2:Structure {key:$s2})
        MATCH (s1:Structure {key:$s1})

        MERGE (s3)-[:SUB_STRUCTURE_OF {label_ja:"下位構造"}]->(s2)
        MERGE (s2)-[:SUB_STRUCTURE_OF {label_ja:"下位構造"}]->(s1)
        """,
        s3=s3_key,
        s2=s2_key,
        s1=s1_key
        )

# =========================
# embedding
# =========================

embedding_cache = {}

def get_embedding(text):

    if text in embedding_cache:
        return embedding_cache[text]

    vec = get_embedder().encode(text)

    embedding_cache[text] = vec

    return vec

def safe_embedding(e):
    if e is None:
        return np.zeros(384)  # embedding の次元に合わせてゼロベクトル
    elif isinstance(e, str):
        e = e.strip()
        if not e:
            return np.zeros(384)
        try:
            # 文字列がリスト形式の場合は literal_eval
            return np.array(ast.literal_eval(e), dtype=float)
        except (ValueError, SyntaxError):
            # 空文字や不正文字列の場合はゼロベクトル
            return np.zeros(384)
    elif isinstance(e, list):
        return np.array(e, dtype=float)
    elif hasattr(e, "tolist"):  # ndarray
        return np.array(e, dtype=float)
    else:
        # 不明な型の場合もゼロベクトルで保護
        return np.zeros(384)

def get_structure_embedding(text):
    return get_embedding(text)

# =========================
# Concept Similarity Kernel
# =========================

def similarity_kernel(v1, v2):

    if v1 is None or v2 is None:
        return 0.0

    v1 = safe_embedding(v1)
    v2 = safe_embedding(v2)

    denom = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denom == 0:
        return 0.0

    return np.dot(v1, v2) / denom

# =========================
# Structure取得
# =========================

def fetch_structures(level=None):

    with get_driver().session() as session:

        if level:
            result = session.run("""
            MATCH (s:Structure)
            WHERE s.level = $level
            RETURN s.key AS key,
            s.name_ja AS name,
            s.embedding AS embedding
            """, level=level)
        else:
            result = session.run("""
            MATCH (s:Structure)
            RETURN s.key AS key,
            s.name_ja AS name,
            s.embedding AS embedding
            """)

        data = []

        for r in result:
            data.append({
                "key": r["key"],
                "name": r["name"],
                "embedding": safe_embedding(r["embedding"])
            })

        return data

# =========================
# 類似Structure検索
# =========================

def find_similar_structures(query_vec, structures, level, top_k=5):

    threshold_map = {
        3: 0.7,
        2: 0.7,
        1: 0.6
    }

    threshold = threshold_map.get(level, 0.7)

    scored = []

    for s in structures:
        sim = similarity_kernel(query_vec, s["embedding"])
        scored.append((sim, s))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [s for sim, s in scored[:top_k] if sim > threshold]

# =========================
# LLM正規化
# =========================

def normalize_structure_name(name):

    prompt = f"""
次の構造を標準化せよ。

条件：
・英語（snake_case）でkeyを生成
・分野非依存の一般概念
・既存概念のみ（新語禁止）

さらに：
・対応する自然な日本語名も生成せよ
・keyとname_jaは意味的に1対1対応させること

入力:
{name}

出力は必ずJSON：

{{
  "key": "",
  "name_ja": ""
}}
"""

    res = call_llm(prompt, tag="normalize_structure")

    data = parse_llm_json(res.text)

    if not data:
        # fallback
        key = name.strip().lower().replace(" ", "_")
        return key, name

    key = data["key"].strip().lower().replace(" ", "_")
    name_ja = data["name_ja"].strip()

    return key, name_ja

# =========================
# LLM同一性判定
# =========================

def llm_structure_match(query_name, candidates):

    if not candidates:
        return None

    candidate_text = "\n".join([
        f"{i}: {c['name']}"
        for i, c in enumerate(candidates)
    ])

    prompt = f"""
次の構造が既存構造と同一か判定せよ。

新規:
{query_name}

候補:
{candidate_text}

条件：
・意味が同じなら同一
・違えば NONE

出力:
番号 または NONE
"""

    res = call_llm(prompt, tag="structure_match")

    out = res.text.strip()

    if out == "NONE":
        return None

    try:
        idx = int(out)
        return candidates[idx]
    except:
        return None

# =========================
# Structure解決（核心）
# =========================

def resolve_structure(structure_input, level):

    # ① normalizeで両方取得
    normalized, name_ja = normalize_structure_name(structure_input)

    # ② embedding（英語key）
    query_vec = get_structure_embedding(normalized)

    # ③ DB取得
    existing = fetch_structures(level=level)

    # ④ 類似検索
    candidates = find_similar_structures(query_vec, existing, level)

    # ⑤ LLM同一性判定
    matched = llm_structure_match(structure_input, candidates)

    if matched:
        return matched["key"], matched["name"], matched["embedding"]

    # 新規
    return normalized, name_ja, query_vec

# =========================
# Graph書き込み
# =========================

def write_graph_minimal(concept_name, description, modes_json):

    with get_driver().session() as session:

        # --- Concept ---
        desc_data = generate_description(concept_name)

        description = desc_data["description"]
        domain = desc_data["domain"]

        color = DOMAIN_COLOR_MAP.get(domain, "#CCCCCC")

        session.run("""
        MERGE (c:Concept {name:$name})
        SET c.description = $desc,
            c.domain = $domain,
            c.color = $color
        """,
        name=concept_name,
        desc=description,
        domain=domain,
        color=color
        )
        

        for mode in modes_json["modes"]:

            type_key = mode["type"]
            type_ja = MODE_TYPE_MAP.get(type_key, type_key)

            # --- Mode ---
            result = session.run("""
            MATCH (c:Concept {name:$concept})

            MERGE (c)-[:HAS_MODE]->(m:Mode {type_key:$type_key})
            SET m.type_ja = $type_ja,
                m.状態 = $state,
                m.変換 = $transformation,
                m.制約 = $constraint,
                m.動的法則 = $dynamics,
                m.フィードバック = $feedback,
                m.破綻 = $failure

            RETURN elementId(m) as mid
            """,
            concept=concept_name,
            type_key=type_key,
            type_ja=type_ja,
            state=str(mode["state"]),
            transformation=mode["transformation"],
            constraint=mode["constraint"],
            dynamics=mode["dynamics"],
            feedback=mode["feedback"],
            failure=mode["failure"]
            )

            mid = result.single()["mid"]

            # =========================
            # Structure統合（収束）
            # =========================

            structure_ja = mode["structure"]

            structure_key, resolved_name, emb = resolve_structure(structure_ja, level=3)

            session.run("""
            MERGE (s:Structure {key:$key})
            SET s.name_ja = $name,
                s.embedding = $embedding,
                s.level = 3
            """,
            key=structure_key,
            name=resolved_name,
            embedding=emb.tolist()
            )

            # ★ここ追加
            build_structure_hierarchy(structure_key, resolved_name)

            # Mode → Structure
            session.run("""
            MATCH (m) WHERE elementId(m) = $mid
            MATCH (s:Structure {key:$key})

            MERGE (m)-[:INSTANCE_OF {
                label_ja:$label
            }]->(s)
            """,
            mid=mid,
            key=structure_key,
            label=EDGE_LABELS["INSTANCE_OF"]
            )

def summarize_llm_stats(stats):

    total_calls = 0
    total_prompt = 0
    total_response = 0

    for tag, s in stats.items():
        total_calls += s["calls"]
        total_prompt += s["prompt_tokens"]
        total_response += s["response_tokens"]

    return {
        "total_calls": total_calls,
        "total_prompt_tokens": total_prompt,
        "total_response_tokens": total_response,
        "total_tokens": total_prompt + total_response
    }

# =========================
# パイプライン
# =========================

def run_pipeline(concept):

    global LLM_STATS
    LLM_STATS = {} 

    log_step("Generating modes")
    modes_json = generate_modes(concept)

    if not modes_json:
        print("Mode生成失敗")
        return

    log_step("Generating description")
    description = generate_description(concept)

    log_step("Writing graph")
    write_graph_minimal(concept, description, modes_json)

    print("\rPipeline実行完了！")

    return {
    "concept": concept,
    "modes": modes_json,
    "llm_stats": LLM_STATS
}

#if __name__ == "__main__":

    concept = "ユークリッド距離"  

    result = run_pipeline(concept)

    # --- 集計 ---
    summary = summarize_llm_stats(result["llm_stats"])

    # --- 出力 ---
    print("\n=== RESULT ===")
    print(json.dumps(result["modes"], ensure_ascii=False, indent=2))

    print("\n=== LLM STATS (DETAIL) ===")
    print(json.dumps(result["llm_stats"], ensure_ascii=False, indent=2))

    print("\n=== LLM STATS (SUMMARY) ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))