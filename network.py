"""
network.py — CBIS / BiblioX Network Analytics
---------------------------------------------
Generates co-authorship and keyword co-occurrence networks with
interactive and static visualization support.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

from __future__ import annotations
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import Counter
from themes import current_palette, mm_to_inches, FIG_SIZES_MM

# ============================================================
# 1. UTILITIES
# ============================================================
def _normalize_entities(txt: str) -> list[str]:
    if not isinstance(txt, str):
        return []
    return [t.strip() for t in txt.split(";") if t.strip()]

def _subgraph_prune(G: nx.Graph, min_degree: int = 2) -> nx.Graph:
    keep = [n for n, d in dict(G.degree()).items() if d >= min_degree]
    return G.subgraph(keep).copy()

def _compute_network_stats(G: nx.Graph) -> dict:
    if G.number_of_nodes() == 0:
        return {"nodes": 0, "edges": 0}
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": nx.density(G),
        "avg_degree": np.mean([d for _, d in G.degree()]),
        "components": nx.number_connected_components(G),
    }

# ============================================================
# 2. CO-AUTHORSHIP NETWORK
# ============================================================
def coauthorship_graph(df: pd.DataFrame, min_freq: int = 2) -> nx.Graph:
    """Build co-authorship network; nodes=authors, edges=co-publications."""
    G = nx.Graph()
    for row in df["authors"].fillna(""):
        authors = sorted(set(_normalize_entities(row)))
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                a, b = authors[i], authors[j]
                w = G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1
                G.add_edge(a, b, weight=w)
    G2 = _subgraph_prune(G, min_freq)
    nx.set_node_attributes(G2, dict(G2.degree()), "degree")
    return G2

# ============================================================
# 3. KEYWORD CO-OCCURRENCE NETWORK
# ============================================================
def keyword_cooccurrence_graph(
    df: pd.DataFrame, field="author_keywords", min_freq=3
) -> tuple[nx.Graph, pd.Series]:
    """Build keyword co-occurrence network."""
    freq = Counter()
    G = nx.Graph()

    for row in df[field]:
        if not isinstance(row, list) or len(row) < 2:
            continue
        row = sorted(set(row))
        for kw in row:
            freq[kw] += 1
        for i in range(len(row)):
            for j in range(i + 1, len(row)):
                a, b = row[i], row[j]
                w = G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1
                G.add_edge(a, b, weight=w)

    nodes = {k for k, v in freq.items() if v >= min_freq}
    G2 = G.subgraph(nodes).copy()
    nx.set_node_attributes(G2, {k: {"freq": freq[k]} for k in nodes})
    nx.set_node_attributes(G2, dict(G2.degree()), "degree")
    return G2, pd.Series(freq).sort_values(ascending=False)

# ============================================================
# 4. COMMUNITY DETECTION (OPTIONAL)
# ============================================================
def detect_communities(G: nx.Graph) -> dict[str, int]:
    """Detect communities using Louvain if available; fallback to greedy."""
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(G)
    except Exception:
        partition = nx.algorithms.community.greedy_modularity_communities(G)
        partition = {n: i for i, comm in enumerate(partition) for n in comm}
    nx.set_node_attributes(G, partition, "community")
    return partition

# ============================================================
# 5. STATIC VISUALIZATION (PUBLICATION-GRADE)
# ============================================================
def plot_network_static(
    G: nx.Graph,
    layout: str = "spring",
    size_key: str = "degree",
    color_by: str = "community",
    size_key_scale: float = 20,
    size_key_min: float = 30,
    figsize_key: str = "one_half",
    show_labels: bool = False,
):
    """Static Matplotlib visualization for publication export."""
    if G.number_of_nodes() == 0:
        raise ValueError("Empty graph — nothing to plot.")

    wmm, hmm = FIG_SIZES_MM[figsize_key]
    fig, ax = plt.subplots(figsize=(mm_to_inches(wmm), mm_to_inches(hmm)))
    pos = (
        nx.spring_layout(G, k=0.35, seed=42)
        if layout == "spring"
        else nx.kamada_kawai_layout(G)
    )

    # Node sizes & colors
    sizes = np.array([G.nodes[n].get(size_key, 1) for n in G.nodes()])
    sizes = np.clip(size_key_min + sizes * size_key_scale, size_key_min, 500)
    if color_by == "community" and "community" in nx.get_node_attributes(G, "community"):
        comms = [G.nodes[n]["community"] for n in G.nodes()]
        colors = np.array(current_palette(len(set(comms))))[
            [c % len(current_palette()) for c in comms]
        ]
    else:
        colors = current_palette(1) * G.number_of_nodes()

    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=0.4, alpha=0.5)
    if show_labels:
        nx.draw_networkx_labels(G, pos, font_size=6, font_family="Times New Roman")

    ax.axis("off")
    fig.tight_layout(pad=0.01)
    return fig

# ============================================================
# 6. PYVIS INTERACTIVE EXPORT
# ============================================================
def export_pyvis_html(G: nx.Graph, path="network.html", physics=True) -> str:
    """Save interactive HTML network using PyVis."""
    try:
        from pyvis.network import Network
        net = Network(height="750px", width="100%", notebook=False, directed=False)
        if physics:
            net.barnes_hut(gravity=-25000, central_gravity=0.3, spring_length=150)
        else:
            net.force_atlas_2based()

        for n, data in G.nodes(data=True):
            label = n
            size = 5 + 2 * data.get("degree", 1)
            color = current_palette(1)[0]
            net.add_node(n, label=label, value=size, color=color)

        for u, v, data in G.edges(data=True):
            net.add_edge(u, v, value=data.get("weight", 1))

        net.show(path)
        return str(Path(path).resolve())
    except Exception as e:
        return f"[ERROR] PyVis export failed: {e}"

# ============================================================
# 7. EXPORT NETWORK STRUCTURES
# ============================================================
def export_network(G: nx.Graph, base_name="network"):
    """Export to multiple formats (.graphml, .gexf, .html)."""
    base = Path(base_name)
    nx.write_graphml(G, base.with_suffix(".graphml"))
    nx.write_gexf(G, base.with_suffix(".gexf"))
    export_pyvis_html(G, base.with_suffix(".html"))
    print(f"[INFO] Exported network → {base}.[graphml/gexf/html]")

# ============================================================
# 8. DEMO
# ============================================================
def _demo():
    data = {
        "authors": [
            "A;B;C", "A;B", "B;C;D", "A;E", "D;E;F", "C;F;G"
        ]
    }
    df = pd.DataFrame(data)
    G = coauthorship_graph(df, min_freq=1)
    detect_communities(G)
    fig = plot_network_static(G, show_labels=True)
    fig.savefig("demo_network.png", dpi=600, bbox_inches="tight")
    export_network(G, "demo_network")
    print("✅ Demo co-authorship network generated.")

if __name__ == "__main__":
    _demo()
