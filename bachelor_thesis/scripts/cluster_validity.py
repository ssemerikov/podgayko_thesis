"""
Internal cluster validity metrics for VOSViewer (4-cluster) and
Python-Louvain (best-fit) partitions of the 28-keyword co-occurrence
network. Computes:

  - Newman modularity Q (network-based, requires the graph)
  - Silhouette coefficient (vector-based, on cooccurrence-distance matrix)
  - Stability of Louvain over 100 runs at the best resolution
    (variance of partition via mean pairwise ARI)

Outputs human-readable summary to stdout and writes
`bachelor_thesis/data/cluster_validity.csv` for thesis import.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import community as community_louvain
from sklearn.metrics import adjusted_rand_score, silhouette_score

from wos_parser import load_savedrecs, load_vosviewer_map, ROOT_DIR
from clustering import build_cooccurrence_matrix


def newman_modularity(G: nx.Graph, partition: dict[str, int]) -> float:
    """Newman-Girvan modularity Q for a weighted graph and node partition."""
    return community_louvain.modularity(partition, G, weight="weight")


def silhouette_on_cooccurrence(cooc: np.ndarray, labels: list[int]) -> float:
    """Silhouette coefficient using a distance derived from co-occurrence.

    Distance d_ij = 1 / (1 + cooc_ij) — bounded in (0, 1], 0 means
    perfect co-occurrence. A precomputed distance matrix is fed to
    sklearn's silhouette with metric='precomputed'.
    """
    n = cooc.shape[0]
    dist = 1.0 / (1.0 + cooc.astype(float))
    np.fill_diagonal(dist, 0.0)
    if len(set(labels)) < 2 or len(set(labels)) >= n:
        return float("nan")
    return float(silhouette_score(dist, labels, metric="precomputed"))


def louvain_stability(G: nx.Graph, resolution: float, n_runs: int = 100) -> dict:
    """Run Louvain n_runs times at given resolution; report mean pairwise ARI."""
    partitions: list[list[int]] = []
    nodes = list(G.nodes())
    for seed in range(n_runs):
        p = community_louvain.best_partition(G, resolution=resolution, random_state=seed)
        partitions.append([p[k] for k in nodes])
    pairwise = []
    for i in range(n_runs):
        for j in range(i + 1, n_runs):
            pairwise.append(adjusted_rand_score(partitions[i], partitions[j]))
    return {
        "n_runs": n_runs,
        "mean_pairwise_ari": float(np.mean(pairwise)),
        "std_pairwise_ari": float(np.std(pairwise)),
        "n_unique_partitions": len({tuple(p) for p in partitions}),
    }


def main() -> None:
    df_wos = load_savedrecs()
    df_map = load_vosviewer_map()
    keywords = df_map["label"].tolist()
    vos_labels_dict = df_map.set_index("label")["cluster"].to_dict()

    cooc = build_cooccurrence_matrix(df_wos, keywords)

    # Build graph
    G = nx.Graph()
    G.add_nodes_from(keywords)
    n = len(keywords)
    for i in range(n):
        for j in range(i + 1, n):
            w = cooc[i][j]
            if w > 0:
                G.add_edge(keywords[i], keywords[j], weight=float(w))

    # VOSViewer 4-cluster partition (from map data)
    vos_partition = {kw: int(vos_labels_dict[kw]) for kw in keywords}
    vos_labels = [vos_partition[kw] for kw in keywords]

    # Python-Louvain best partition (replicate main.py's logic)
    candidates = []
    for r100 in range(50, 201):
        r = r100 / 100.0
        partition = community_louvain.best_partition(G, resolution=r, random_state=42)
        nc = len(set(partition.values()))
        if 3 <= nc <= 5:
            py_lab = [partition[kw] for kw in keywords]
            ari = adjusted_rand_score(vos_labels, py_lab)
            sizes = pd.Series(list(partition.values())).value_counts()
            if sizes.min() >= 2:
                candidates.append((r, nc, partition, ari))
    candidates.sort(key=lambda x: x[3], reverse=True)
    best_r, best_nc, py_partition, best_ari = candidates[0]
    for r, nc, partition, ari in candidates:
        if nc == 4 and ari >= best_ari - 0.05:
            best_r, best_nc, py_partition, best_ari = r, nc, partition, ari
            break
    py_labels = [py_partition[kw] for kw in keywords]

    print(f"Best Louvain resolution: {best_r:.2f}; clusters: {best_nc}; ARI={best_ari:.3f}")
    print()

    # Validity metrics
    Q_vos = newman_modularity(G, vos_partition)
    Q_py = newman_modularity(G, py_partition)
    sil_vos = silhouette_on_cooccurrence(cooc, vos_labels)
    sil_py = silhouette_on_cooccurrence(cooc, py_labels)

    print("Internal validity:")
    print(f"  Newman Q (VOSViewer 4-cluster) = {Q_vos:.4f}")
    print(f"  Newman Q (Python-Louvain {best_nc}-cluster) = {Q_py:.4f}")
    print(f"  Silhouette (VOSViewer 4-cluster) = {sil_vos:.4f}")
    print(f"  Silhouette (Python-Louvain {best_nc}-cluster) = {sil_py:.4f}")
    print()

    stab = louvain_stability(G, resolution=best_r, n_runs=100)
    print(f"Louvain stability over {stab['n_runs']} runs at r={best_r:.2f}:")
    print(f"  mean pairwise ARI = {stab['mean_pairwise_ari']:.3f} (SD={stab['std_pairwise_ari']:.3f})")
    print(f"  unique partitions = {stab['n_unique_partitions']}")

    # Save CSV for thesis import
    out = ROOT_DIR / "data" / "cluster_validity.csv"
    out.parent.mkdir(exist_ok=True)
    pd.DataFrame(
        [
            {"method": "VOSViewer", "n_clusters": 4, "Q": Q_vos, "silhouette": sil_vos},
            {
                "method": "Python-Louvain",
                "n_clusters": best_nc,
                "Q": Q_py,
                "silhouette": sil_py,
                "stability_mean_ari": stab["mean_pairwise_ari"],
                "stability_sd_ari": stab["std_pairwise_ari"],
                "stability_unique_partitions": stab["n_unique_partitions"],
            },
        ]
    ).to_csv(out, index=False, encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
