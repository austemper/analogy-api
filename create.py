import os
import re
import json
from neo4j import GraphDatabase
from google import genai

# =========================
# 設定
# =========================

NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+ssc://cb753f8e.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "cb753f8e")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# 共通
# =========================

def call_llm(prompt):
    res = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return res.text if res.text else ""


def parse_json(text):
    text = text.replace("```json", "").replace("```", "")
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except:
        return None

# =========================
# Concept: necessity
# =========================

def generate_necessity(concept):

    prompt = f"""
次の概念の存在必要性を1文で述べよ。

概念:
{concept}

条件：
・1文
・必ず「何の問題を防ぐ／何の損失を回避するか」を含める
・可能なら「導入しない場合に起こる具体的な不利益」を明示
・抽象語（効率化・最適化など）だけで終わらせない
・機能説明（どう動くか）は禁止
・結果・帰結ベースで書く（outcomeベース）


悪い例：
「効率を向上させるために必要」
（抽象的すぎる）


良い例：
「ピーク電力による契約コスト増大と設備過負荷を回避するために必要」


出力JSON:
{{
  "necessity": ""
}}
"""

    data = parse_json(call_llm(prompt))

    if not data:
        return "存在理由不明"

    return data.get("necessity", "存在理由不明")

# =========================
# Structure: description
# =========================

def generate_structure_description(name):

    prompt = f"""
次の構造を平易に説明せよ。

構造:
{name}

条件：
・1文
・中学生でも理解できる
・抽象すぎない
・具体例は禁止（構造の本質のみ）

出力JSON:
{{
  "description": ""
}}
"""

    data = parse_json(call_llm(prompt))

    if not data:
        return "説明なし"

    return data.get("description", "説明なし")

# =========================
# DB取得
# =========================

def fetch_concepts(overwrite=False):

    with driver.session() as session:

        if overwrite:
            q = "MATCH (c:Concept) RETURN c.name AS name"
        else:
            q = """
            MATCH (c:Concept)
            WHERE c.necessity IS NULL OR c.necessity = ""
            RETURN c.name AS name
            """

        return [r["name"] for r in session.run(q)]


def fetch_structures(overwrite=True):

    with driver.session() as session:

        if overwrite:
            q = """
            MATCH (s:Structure)
            WHERE s.level = 3
            RETURN s.key AS key, s.name_ja AS name
            """
        else:
            q = """
            MATCH (s:Structure)
            WHERE s.level = 3
            AND (s.description IS NULL OR s.description = "")
            RETURN s.key AS key, s.name_ja AS name
            """

        return [{"key": r["key"], "name": r["name"]} for r in session.run(q)]

# =========================
# DB更新
# =========================

def update_necessity(concept, necessity):

    with driver.session() as session:
        session.run("""
        MATCH (c:Concept {name:$name})
        SET c.necessity = $val
        """, name=concept, val=necessity)


def update_structure_description(key, desc):

    with driver.session() as session:
        session.run("""
        MATCH (s:Structure {key:$key})
        SET s.description = $desc
        """, key=key, desc=desc)

# =========================
# メイン
# =========================

def main():

    concepts = fetch_concepts(overwrite=False)
    structures = fetch_structures(overwrite=False)

    print(f"Concept: {len(concepts)}, Structure: {len(structures)}")

    # --- Concept ---
    for i, c in enumerate(concepts):
        print(f"[C {i+1}/{len(concepts)}] {c}", end="\r")

        try:
            val = generate_necessity(c)
            update_necessity(c, val)
        except Exception as e:
            print(f"\nERROR Concept {c}: {e}")

    # --- Structure ---
    for i, s in enumerate(structures):
        print(f"[S {i+1}/{len(structures)}] {s['name']}", end="\r")

        try:
            desc = generate_structure_description(s["name"])
            update_structure_description(s["key"], desc)
        except Exception as e:
            print(f"\nERROR Structure {s['name']}: {e}")

    print("\nDONE")

# =========================

if __name__ == "__main__":
    main()