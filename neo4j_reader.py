import os
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    os.environ.get("NEO4J_URI", "neo4j+ssc://cb753f8e.databases.neo4j.io"),
    auth=(
        os.environ.get("NEO4J_USER", "cb753f8e"),
        os.environ.get("NEO4J_PASSWORD", "")
    )
)

def get_graph(tx):
    return tx.run("""
        MATCH (n)-[r]->(m)
        RETURN
            id(n) AS src,
            id(m) AS dst,
            labels(n) AS src_labels,
            labels(m) AS dst_labels,
            properties(n) AS src_props,
            properties(m) AS dst_props,
            type(r) AS rel_type,
            properties(r) AS rel_props
        LIMIT 100000
    """).data()


def fetch_graph():
    with driver.session() as session:
        return session.execute_read(get_graph)