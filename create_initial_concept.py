import ast
import certifi
import ssl
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

uri = "neo4j+s://cb753f8e.databases.neo4j.io"
user = "cb753f8e"
password = "jZjomf52EraNedkSD6kPus1OVRbj9Oo0pCeUu1Dhn3M"

driver = GraphDatabase.driver(
    uri,
    auth=(user, password)
)

with driver.session() as session:
    print(session.run("RETURN 1").single())


# ドメインカラーのマッピング例
DOMAIN_COLOR_MAP = {
    "physical": "#FF6666",
    "chemical": "#66CCFF",
    "biological": "#66FF66",
    "neural": "#FFCC66",
    "cognitive": "#CC66FF",
    "social": "#FF9966",
    "informational": "#66FFFF",
    "formal": "#999999",
    "mathematical": "#FFCCFF",
    "philosophical": "#CCCCFF"
}

embedder = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

initial_concepts_100 = [
{"name":"エネルギー","domain_type":["physical"],"abstraction_level":4,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"物理的作業や変化の能力"},
{"name":"運動","domain_type":["physical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"物体の位置が時間とともに変化する現象"},
{"name":"熱","domain_type":["physical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"物質の温度に関連するエネルギーの総和"},
{"name":"力","domain_type":["physical"],"abstraction_level":4,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"物体に加わる作用、変形や運動を引き起こす"},
{"name":"質量","domain_type":["physical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"物体の量的尺度"},
{"name":"重力","domain_type":["physical"],"abstraction_level":4,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"物体間に働く引力"},
{"name":"電磁気","domain_type":["physical","formal"],"abstraction_level":5,"universality":7,"reality_level":2,"year":18,"embedding":None,"description":"電気・磁気現象の理論体系"},
{"name":"波動","domain_type":["physical"],"abstraction_level":4,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"振動が媒質を通じて伝わる現象"},
{"name":"光","domain_type":["physical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"可視電磁波"},
{"name":"音","domain_type":["physical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":0,"embedding":None,"description":"空気などの媒質の振動として伝わる波"},
{"name":"原子","domain_type":["chemical","physical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":19,"embedding":None,"description":"化学元素の基本単位"},
{"name":"分子","domain_type":["chemical"],"abstraction_level":3,"universality":7,"reality_level":2,"year":19,"embedding":None,"description":"原子が結合して形成される化学単位"},
{"name":"化学結合","domain_type":["chemical"],"abstraction_level":4,"universality":7,"reality_level":2,"year":19,"embedding":None,"description":"原子同士を結びつける相互作用"},
{"name":"反応速度","domain_type":["chemical"],"abstraction_level":4,"universality":6,"reality_level":2,"year":19,"embedding":None,"description":"化学反応の進行速度"},
{"name":"触媒","domain_type":["chemical"],"abstraction_level":4,"universality":6,"reality_level":2,"year":19,"embedding":None,"description":"反応速度を変えるが消費されない物質"},
{"name":"酵素","domain_type":["biological","chemical"],"abstraction_level":4,"universality":6,"reality_level":6,"year":19,"embedding":None,"description":"生体触媒"},
{"name":"細胞","domain_type":["biological"],"abstraction_level":3,"universality":7,"reality_level":6,"year":17,"embedding":None,"description":"生命の基本単位"},
{"name":"遺伝子","domain_type":["biological","informational"],"abstraction_level":4,"universality":7,"reality_level":6,"year":19,"embedding":None,"description":"生物の形質を決めるDNAの単位"},
{"name":"DNA","domain_type":["biological","chemical"],"abstraction_level":4,"universality":7,"reality_level":6,"year":20,"embedding":None,"description":"遺伝情報を担う二重らせん構造"},
{"name":"進化","domain_type":["biological"],"abstraction_level":5,"universality":7,"reality_level":6,"year":19,"embedding":None,"description":"生物種が時間とともに変化する過程"},
{"name":"神経","domain_type":["biological","neural"],"abstraction_level":3,"universality":6,"reality_level":6,"year":17,"embedding":None,"description":"情報伝達を行う細胞群"},
{"name":"ニューロン","domain_type":["neural","biological"],"abstraction_level":3,"universality":6,"reality_level":6,"year":19,"embedding":None,"description":"神経系の基本単位"},
{"name":"シナプス","domain_type":["neural"],"abstraction_level":4,"universality":6,"reality_level":6,"year":19,"embedding":None,"description":"ニューロン間の接続部"},
{"name":"認知","domain_type":["cognitive","neural"],"abstraction_level":5,"universality":8,"reality_level":6,"year":20,"embedding":None,"description":"情報を知覚・理解・記憶・判断する過程"},
{"name":"記憶","domain_type":["cognitive","neural"],"abstraction_level":4,"universality":8,"reality_level":6,"year":19,"embedding":None,"description":"情報を保持・再生する機能"},
{"name":"学習","domain_type":["cognitive","neural"],"abstraction_level":5,"universality":8,"reality_level":6,"year":19,"embedding":None,"description":"経験から知識や技能を獲得する過程"},
{"name":"意識","domain_type":["cognitive","philosophical"],"abstraction_level":6,"universality":9,"reality_level":6,"year":0,"embedding":None,"description":"自己や環境の知覚"},
{"name":"感情","domain_type":["cognitive","biological"],"abstraction_level":5,"universality":8,"reality_level":6,"year":0,"embedding":None,"description":"情動の生理的・心理的表現"},
{"name":"社会","domain_type":["social"],"abstraction_level":6,"universality":9,"reality_level":7,"year":0,"embedding":None,"description":"人間の集団活動"},
{"name":"文化","domain_type":["social","philosophical"],"abstraction_level":6,"universality":9,"reality_level":7,"year":0,"embedding":None,"description":"集団の知識・信念・慣習の総体"},
{"name":"言語","domain_type":["cognitive","informational","social"],"abstraction_level":5,"universality":9,"reality_level":7,"year":0,"embedding":None,"description":"意味を伝える体系的記号"},
{"name":"コミュニケーション","domain_type":["social","informational"],"abstraction_level":5,"universality":9,"reality_level":7,"year":0,"embedding":None,"description":"情報や感情のやり取り"},
{"name":"法","domain_type":["social","philosophical"],"abstraction_level":6,"universality":9,"reality_level":7,"year":17,"embedding":None,"description":"社会秩序を規律する規範"},
{"name":"経済","domain_type":["social"],"abstraction_level":6,"universality":9,"reality_level":7,"year":17,"embedding":None,"description":"資源配分と人間活動の体系"},
{"name":"数学","domain_type":["formal"],"abstraction_level":6,"universality":10,"reality_level":4,"year":0,"embedding":None,"description":"量・構造・変化を形式的に扱う学問"},
{"name":"集合論","domain_type":["formal","mathematical"],"abstraction_level":7,"universality":10,"reality_level":4,"year":19,"embedding":None,"description":"集合の性質と操作を扱う理論"},
{"name":"論理","domain_type":["formal","philosophical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":0,"embedding":None,"description":"正しい推論の形式体系"},
{"name":"アルゴリズム","domain_type":["informational","formal"],"abstraction_level":6,"universality":9,"reality_level":4,"year":20,"embedding":None,"description":"計算手順の体系"},
{"name":"情報理論","domain_type":["informational","formal"],"abstraction_level":6,"universality":9,"reality_level":4,"year":20,"embedding":None,"description":"情報の量と伝達を数学的に扱う理論"},
{"name":"データ構造","domain_type":["informational","formal"],"abstraction_level":6,"universality":9,"reality_level":4,"year":20,"embedding":None,"description":"データの整理と管理の方法"},
{"name":"確率","domain_type":["formal","mathematical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":17,"embedding":None,"description":"不確実性を定量化する数学概念"},
{"name":"統計","domain_type":["formal","mathematical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":18,"embedding":None,"description":"データの分析と解釈"},
{"name":"ポアソン分布","domain_type":["formal","mathematical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":19,"embedding":None,"description":"離散確率分布の一種"},
{"name":"ガウス分布","domain_type":["formal","mathematical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":18,"embedding":None,"description":"正規分布"},
{"name":"最適化","domain_type":["formal","mathematical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":20,"embedding":None,"description":"目的関数の最大化・最小化"},
{"name":"ネットワーク理論","domain_type":["formal","informational"],"abstraction_level":6,"universality":9,"reality_level":5,"year":20,"embedding":None,"description":"ノードとリンクの構造解析"},
{"name":"複雑系","domain_type":["formal","physical","social"],"abstraction_level":7,"universality":9,"reality_level":5,"year":20,"embedding":None,"description":"多数要素の相互作用による非線形現象"},
{"name":"フィードバック","domain_type":["formal","physical","social"],"abstraction_level":5,"universality":9,"reality_level":5,"year":0,"embedding":None,"description":"出力が入力に影響する仕組み"},
{"name":"カオス","domain_type":["physical","mathematical"],"abstraction_level":7,"universality":9,"reality_level":4,"year":20,"embedding":None,"description":"非線形系の予測困難な振る舞い"},
{"name":"自己組織化","domain_type":["physical","biological","social"],"abstraction_level":7,"universality":9,"reality_level":5,"year":20,"embedding":None,"description":"局所相互作用から秩序が自然に生じる現象"},
{"name":"フラクタル","domain_type":["mathematical","physical"],"abstraction_level":7,"universality":9,"reality_level":4,"year":20,"embedding":None,"description":"自己相似構造"},
{"name":"ゲーム理論","domain_type":["formal","social"],"abstraction_level":6,"universality":9,"reality_level":7,"year":20,"embedding":None,"description":"戦略的意思決定の数学的理論"},
{"name":"選択理論","domain_type":["formal","social"],"abstraction_level":6,"universality":9,"reality_level":7,"year":20,"embedding":None,"description":"意思決定に関する理論"},
{"name":"意思決定","domain_type":["cognitive","social"],"abstraction_level":5,"universality":9,"reality_level":7,"year":0,"embedding":None,"description":"複数の選択肢から選ぶ過程"},
{"name":"リスク","domain_type":["formal","social"],"abstraction_level":5,"universality":9,"reality_level":7,"year":0,"embedding":None,"description":"不確実性に伴う損失の可能性"},
{"name":"システム","domain_type":["formal","physical","social"],"abstraction_level":5,"universality":9,"reality_level":5,"year":0,"embedding":None,"description":"要素間の相互作用を持つ全体"},
{"name":"モデル","domain_type":["formal","philosophical"],"abstraction_level":5,"universality":9,"reality_level":5,"year":0,"embedding":None,"description":"現実の抽象化表現"},
{"name":"抽象化","domain_type":["philosophical","formal"],"abstraction_level":9,"universality":10,"reality_level":4,"year":0,"embedding":None,"description":"共通性を抽出し本質を表現する行為"},
{"name":"因果関係","domain_type":["formal","philosophical"],"abstraction_level":6,"universality":10,"reality_level":5,"year":0,"embedding":None,"description":"出来事間の原因と結果の関係"},
{"name":"相関","domain_type":["formal","mathematical"],"abstraction_level":6,"universality":10,"reality_level":4,"year":0,"embedding":None,"description":"二つの事象の同時変動の関係"},
{"name":"確率過程","domain_type":["mathematical","formal"],"abstraction_level":6,"universality":10,"reality_level":4,"year":20,"embedding":None,"description":"時間依存の確率的変動"},
{"name":"情報量","domain_type":["informational","formal"],"abstraction_level":6,"universality":10,"reality_level":4,"year":20,"embedding":None,"description":"情報の量的尺度"},
{"name":"符号化","domain_type":["informational","formal"],"abstraction_level":6,"universality":10,"reality_level":4,"year":20,"embedding":None,"description":"情報を表現形式に変換すること"},
{"name":"圧縮","domain_type":["informational","formal"],"abstraction_level":6,"universality":10,"reality_level":4,"year":20,"embedding":None,"description":"情報量を減らす処理"},
{"name":"アルゴリズム設計","domain_type":["informational","formal"],"abstraction_level":6,"universality":10,"reality_level":4,"year":20,"embedding":None,"description":"問題解決手順の構築"},
{"name":"ソフトウェア","domain_type":["informational","formal"],"abstraction_level":5,"universality":9,"reality_level":5,"year":20,"embedding":None,"description":"計算機上で動作するプログラム"},
{"name":"ハードウェア","domain_type":["physical","informational"],"abstraction_level":4,"universality":9,"reality_level":2,"year":20,"embedding":None,"description":"計算機の物理部品"},
{"name":"ネットワーク","domain_type":["informational","social"],"abstraction_level":5,"universality":9,"reality_level":5,"year":20,"embedding":None,"description":"要素間の接続構造"},
{"name":"インターネット","domain_type":["informational","social"],"abstraction_level":5,"universality":9,"reality_level":5,"year":20,"embedding":None,"description":"世界規模の情報ネットワーク"},
{"name":"AI","domain_type":["informational","cognitive"],"abstraction_level":6,"universality":9,"reality_level":5,"year":21,"embedding":None,"description":"知能を模倣するシステム"},
{"name":"機械学習","domain_type":["informational","cognitive"],"abstraction_level":6,"universality":9,"reality_level":5,"year":21,"embedding":None,"description":"経験からパターンを学習する手法"},
{"name":"深層学習","domain_type":["informational","cognitive"],"abstraction_level":6,"universality":9,"reality_level":5,"year":21,"embedding":None,"description":"多層ニューラルネットワークを用いた学習"},
{"name":"ロボティクス","domain_type":["physical","informational"],"abstraction_level":5,"universality":9,"reality_level":5,"year":21,"embedding":None,"description":"物理デバイスの自動化"},
{"name":"センサ","domain_type":["physical","informational"],"abstraction_level":4,"universality":8,"reality_level":2,"year":21,"embedding":None,"description":"環境情報"}
]

ZERO_VEC = [0.0] * 384  # embedding の初期値

with driver.session() as session:
    for concept in initial_concepts_100:
        session.run(
            """
            CREATE (c:Concept {
                name: $name,
                domain_type: $domain_type,
                abstraction_level: $abstraction_level,
                universality: $universality,
                reality_level: $reality_level,
                year: $year,
                embedding: $embedding,
                description: $description,
                is_initial: $is_initial
            })
            """,
            name=concept["name"],
            domain_type=concept["domain_type"],
            abstraction_level=concept["abstraction_level"],
            universality=concept["universality"],
            reality_level=concept["reality_level"],
            year=concept["year"],
            embedding=ZERO_VEC,  # ← None の代わりにゼロベクトル
            description=concept["description"],
            is_initial=True
        )

def update_missing_properties(batch_size=100):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Concept)
            WHERE c.embedding IS NULL OR c.domain_color IS NULL
            RETURN c.name AS name, c.domain_type AS domain, id(c) AS id
            LIMIT $batch_size
            """,
            batch_size=batch_size
        )
        records = list(result)
        if not records:
            print("No nodes need updating.")
            return

        texts = [r["name"] for r in records]
        ids = [r["id"] for r in records]
        domain_types = [r["domain"] for r in records]

        # 埋め込みをまとめて生成
        embeddings = embedder.encode(texts)

        # ndarray の場合は list に変換
        processed_embeddings = [emb.tolist() if hasattr(emb, "tolist") else list(emb) for emb in embeddings]

        # ドメインカラー計算
        colors = []
        for dt in domain_types:
            if not dt:
                colors.append("#CCCCCC")
            elif isinstance(dt, list):
                colors.append(DOMAIN_COLOR_MAP.get(dt[0], "#CCCCCC"))
            else:
                colors.append(DOMAIN_COLOR_MAP.get(dt, "#CCCCCC"))

        # UNWIND でまとめて更新
        session.run(
            """
            UNWIND $data AS row
            MATCH (c:Concept)
            WHERE id(c) = row.id
            SET c.embedding = row.embedding,
                c.domain_color = row.color
            """,
            data = [
                        {"id": nid, "embedding": emb, "color": color}
                        for nid, emb, color in zip(ids, processed_embeddings, colors)
                    ]
        )

        print(f"Updated {len(records)} nodes")


# --- 実行 ---
update_missing_properties(batch_size=100)