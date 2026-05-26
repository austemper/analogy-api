import os
import graphistry
import logging

graphistry.register(
    api=3,
    username=os.environ.get("GRAPHISTRY_USERNAME", "austemper.ci"),
    password=os.environ.get("GRAPHISTRY_PASSWORD", "")
)
    

def plot_graph(nodes, edges):
    g = graphistry.nodes(nodes, 'id').edges(edges, 'src', 'dst')

    g = g.bind(source='src', destination='dst')

    logging.info("Graphistryの更新に成功しました！( ^^) _旦~~")

    # ★重要：必ず新規生成（上書き回避）
    g = g.upload()

    url = g.url

    logging.info(f"Graphistry URL: {url}")

    return url