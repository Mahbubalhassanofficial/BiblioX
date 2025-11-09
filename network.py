import networkx as nx
import pandas as pd

def coauthorship_graph(df: pd.DataFrame, min_freq=2):
    """Build co-authorship network; nodes=authors, edge weight=#co-pubs."""
    G = nx.Graph()
    for row in df["authors"].fillna(""):
        authors = [a.strip() for a in str(row).split(";") if a.strip()]
        authors = sorted(set(authors))
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                a,b = authors[i], authors[j]
                w = G[a][b]["weight"]+1 if G.has_edge(a,b) else 1
                G.add_edge(a,b, weight=w)
    # prune low-degree nodes
    deg = dict(G.degree())
    keep = {n for n,d in deg.items() if d >= min_freq}
    G2 = G.subgraph(keep).copy()
    return G2

def keyword_cooccurrence_graph(df: pd.DataFrame, field="author_keywords", min_freq=3):
    from collections import Counter
    freq = Counter()
    G = nx.Graph()
    for row in df[field]:
        if not isinstance(row, list) or len(row) < 2: 
            continue
        row = sorted(set(row))
        for kw in row:
            freq[kw]+=1
        for i in range(len(row)):
            for j in range(i+1, len(row)):
                a,b = row[i], row[j]
                w = G[a][b]["weight"]+1 if G.has_edge(a,b) else 1
                G.add_edge(a,b, weight=w)
    nodes = {k for k,v in freq.items() if v>=min_freq}
    G2 = G.subgraph(nodes).copy()
    nx.set_node_attributes(G2, {k: {"freq":freq[k]} for k in nodes})
    return G2, pd.Series(freq).sort_values(ascending=False)

def export_pyvis_html(G, path="network.html"):
    """Save interactive HTML using PyVis."""
    try:
        from pyvis.network import Network
        net = Network(height="750px", width="100%", notebook=False, directed=False)
        net.barnes_hut()
        for n, data in G.nodes(data=True):
            size = 5 + 2*G.degree(n)
            net.add_node(n, label=n, value=size)
        for u,v,data in G.edges(data=True):
            net.add_edge(u, v, value=data.get("weight",1))
        net.show(path)
        return path
    except Exception as e:
        return f"ERROR: {e}"
