"""Recompute NodeXL network metrics for the #BoycottMcDonalds X network in Python.

Input: a NodeXL Pro workbook export (sheets `Edges` and `Vertices`, header on row 2).
Usage: python src/network_metrics.py data/mcdonald_nodexl.xlsx [--top 5]

Conventions follow NodeXL defaults where documented:
- Vertex names are case-insensitive (lowercased).
- "Tweet" rows are self-loops (an account posting without addressing anyone).
- Degree counts use all non-self-loop edges, duplicates included.
- Betweenness, closeness, eigenvector and clustering use the undirected graph with
  duplicate edges merged and self-loops removed.
- Groups use Clauset-Newman-Moore greedy modularity, as in NodeXL.
"""
import argparse
from pathlib import Path

import networkx as nx
import pandas as pd
from networkx.algorithms.community import greedy_modularity_communities, modularity

ap = argparse.ArgumentParser()
ap.add_argument("workbook")
ap.add_argument("--top", type=int, default=5)
ap.add_argument("--out", default="results")
a = ap.parse_args()
out = Path(a.out); out.mkdir(exist_ok=True)

edges = pd.read_excel(a.workbook, sheet_name="Edges", header=1)
verts = pd.read_excel(a.workbook, sheet_name="Vertices", header=1)
edges = edges.dropna(subset=["Vertex 1", "Vertex 2"])
src = edges["Vertex 1"].astype(str).str.lower()
dst = edges["Vertex 2"].astype(str).str.lower()

M = nx.MultiDiGraph()
M.add_nodes_from(verts["Vertex"].dropna().astype(str).str.lower())
M.add_edges_from(zip(src, dst))
self_loops = nx.number_of_selfloops(M)

D = nx.DiGraph(M)                      # unique directed edges
U = nx.Graph(D); U.remove_edges_from(list(nx.selfloop_edges(U)))
comps = sorted(nx.connected_components(U), key=len, reverse=True)
L = U.subgraph(comps[0])
groups = greedy_modularity_communities(U)

summary = {
    "vertices": M.number_of_nodes(),
    "total_edges": M.number_of_edges(),
    "unique_edges": D.number_of_edges(),
    "edges_with_duplicates": M.number_of_edges() - D.number_of_edges(),
    "self_loops": self_loops,
    "connected_components": len(comps),
    "single_vertex_components": sum(len(c) == 1 for c in comps),
    "largest_component_vertices": L.number_of_nodes(),
    "largest_component_edges": L.number_of_edges(),
    "max_geodesic_distance_largest": nx.diameter(L),
    "avg_geodesic_distance_largest": round(nx.average_shortest_path_length(L), 4),
    "graph_density_directed": round(nx.density(D), 6),
    "groups_cnm": len(groups),
    "modularity_cnm": round(modularity(U, groups), 4),
    "date_min": str(pd.to_datetime(edges["Relationship Date (UTC)"]).min()),
    "date_max": str(pd.to_datetime(edges["Relationship Date (UTC)"]).max()),
}
pd.Series(summary).to_csv(out / "network_summary.csv", header=["value"])
edges["Relationship"].value_counts().to_csv(out / "relationship_types.csv")

def _eig(g):
    # Power iteration on the whole graph, scaled to sum to 1 (NodeXL convention).
    ev = nx.eigenvector_centrality(g, max_iter=5000, tol=1e-9)
    total = sum(ev.values())
    return {k: v / total for k, v in ev.items()}


M_nl = nx.MultiDiGraph(M); M_nl.remove_edges_from(list(nx.selfloop_edges(M_nl)))
D_nl = nx.DiGraph(M_nl)
cent = pd.DataFrame({
    "in_degree": dict(M_nl.in_degree()),
    "out_degree": dict(M_nl.out_degree()),
    "unique_in_degree": dict(D_nl.in_degree()),
    "unique_out_degree": dict(D_nl.out_degree()),
    # NodeXL counts each unordered pair twice, so its values are 2x networkx's.
    "betweenness_nodexl_scale": {k: 2 * v for k, v in nx.betweenness_centrality(U, normalized=False).items()},
    "closeness": nx.closeness_centrality(U),
    "eigenvector": _eig(U),
}).fillna(0)
# Account-level table stays local (contains handles); see .gitignore.
cent.sort_values("betweenness_nodexl_scale", ascending=False).to_csv(out / "centrality_by_account.csv")

for k, v in summary.items():
    print(f"{k:32s} {v}")
for col in cent.columns:
    print(f"\nTop {a.top} by {col}:")
    print(cent[col].sort_values(ascending=False).head(a.top).round(4).to_string())
