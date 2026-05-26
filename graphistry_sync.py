import logging
from neo4j_reader import fetch_graph
from graph_etl import transform_graph
from graphistry_client import plot_graph

def update_graphistry():
    data = fetch_graph()
    nodes, edges = transform_graph(data)

    url = plot_graph(nodes, edges)
    logging.info(f"Graphistry URL: {url}")
    return url