"""
Sensitivity sweep of the VOSViewer text-mining occurrence threshold
across {50, 75, 100, 150, 200}. For each threshold, replicate the
text-mining pipeline, build the co-occurrence graph, run Louvain
clustering, and report:

  - # of terms retained
  - # of edges in the network
  - density (fraction of possible pairs with non-zero co-occurrence)
  - # of Louvain clusters at default resolution=1.0
  - Newman modularity Q

This addresses Reviewer #1's concern (R1-#3) that the threshold ≥100
choice was asserted but not defended; the sweep produces an empirical
defence.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import community as community_louvain

from wos_parser import load_savedrecs, ROOT_DIR
from text_mining import build_frequency_table
from clustering import build_cooccurrence_matrix


def sweep_thresholds(thresholds: list[int]) -> pd.DataFrame:
    df_wos = load_savedrecs()
    print(f"Loaded {len(df_wos)} WoS records")
    freq = build_frequency_table(df_wos)
    print(f"Total unique terms (after thesaurus + stopwords): {len(freq)}")

    rows: list[dict] = []
    for t in thresholds:
        retained = freq[freq >= t]
        terms = retained.index.tolist()
        n = len(terms)
        if n < 2:
            rows.append({"threshold": t, "n_terms": n,
                         "n_edges": 0, "density": float("nan"),
                         "n_clusters": 0, "modularity_Q": float("nan")})
            continue

        cooc = build_cooccurrence_matrix(df_wos, terms)
        G = nx.Graph()
        G.add_nodes_from(terms)
        for i in range(n):
            for j in range(i + 1, n):
                w = cooc[i][j]
                if w > 0:
                    G.add_edge(terms[i], terms[j], weight=float(w))

        n_edges = G.number_of_edges()
        max_edges = n * (n - 1) // 2
        density = n_edges / max_edges if max_edges else float("nan")

        partition = community_louvain.best_partition(G, resolution=1.0, random_state=42)
        n_clusters = len(set(partition.values()))
        Q = community_louvain.modularity(partition, G, weight="weight")

        rows.append({
            "threshold": t,
            "n_terms": n,
            "n_edges": n_edges,
            "density": round(density, 3),
            "n_clusters": n_clusters,
            "modularity_Q": round(Q, 4),
        })
        print(f"  threshold={t:>3d}: n={n:>3d} terms, edges={n_edges:>4d}, "
              f"density={density:.3f}, clusters={n_clusters}, Q={Q:+.4f}")

    return pd.DataFrame(rows)


def main() -> None:
    thresholds = [50, 75, 100, 150, 200]
    df = sweep_thresholds(thresholds)
    out = ROOT_DIR / "data" / "threshold_sensitivity.csv"
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT_DIR)}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
