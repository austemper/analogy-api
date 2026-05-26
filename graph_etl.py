import pandas as pd
import numpy as np

def safe_first(x):
    if isinstance(x, list) and len(x) > 0:
        return x[0]
    return np.nan


def transform_graph(data):

    df = pd.DataFrame(data)

    df = pd.concat([
        df[['src', 'dst', 'src_labels', 'dst_labels', 'rel_type']],
        pd.json_normalize(df['src_props']).add_prefix('src_'),
        pd.json_normalize(df['dst_props']).add_prefix('dst_'),
        pd.json_normalize(df['rel_props']).add_prefix('rel_')
    ], axis=1)

    if 'dst_embedding' in df.columns:
        df['dst_embedding_0'] = df['dst_embedding'].apply(safe_first)

    if 'src_embedding' in df.columns:
        df['src_embedding_0'] = df['src_embedding'].apply(safe_first)

    src_nodes = df[['src'] + [c for c in df.columns if c.startswith('src_')]].copy()
    src_nodes.columns = ['id'] + [c.replace('src_', '') for c in src_nodes.columns if c != 'src']

    dst_nodes = df[['dst'] + [c for c in df.columns if c.startswith('dst_')]].copy()
    dst_nodes.columns = ['id'] + [c.replace('dst_', '') for c in dst_nodes.columns if c != 'dst']

    nodes = pd.concat([src_nodes, dst_nodes]).drop_duplicates('id')

    edges = df[['src', 'dst', 'rel_type']].copy()

    return nodes, edges