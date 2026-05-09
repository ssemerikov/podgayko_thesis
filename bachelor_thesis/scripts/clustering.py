"""
Louvain clustering of keyword co-occurrence network and comparison
with VOSViewer cluster assignments.

Builds a 28×28 co-occurrence matrix from WoS title+abstract text,
sweeps the Louvain resolution parameter to find the best 4-cluster
partition (by ARI with VOSViewer), and produces a confusion-matrix
heatmap saved to media/fig_cluster_comparison.png.
"""

import re

import numpy as np
import pandas as pd
import networkx as nx
import community  # python-louvain
import matplotlib.pyplot as plt
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    confusion_matrix,
)

from wos_parser import load_savedrecs, load_vosviewer_map, MEDIA_DIR, setup_matplotlib

# ── Thesaurus ────────────────────────────────────────────────────────────────
THESAURUS = {
    "vocational": "vet", "tvet": "vet", "apprenticeship": "vet",
    "apprenticeships": "vet", "vocation": "vet", "vocations": "vet",
    "students": "student", "learners": "student", "learner": "student",
    "trainees": "student", "trainee": "student", "pupils": "student",
    "pupil": "student", "apprentice": "student", "apprentices": "student",
    "skills": "skill", "skilled": "skill",
    "teachers": "teacher", "teaching": "teacher",
    "studies": "study", "studying": "study", "studied": "study",
    "schools": "school", "schooling": "school",
    "assessments": "assessment", "assessed": "assessment", "assessing": "assessment",
    "models": "model", "modelling": "model", "modeling": "model",
    "modeled": "model", "modelled": "model",
    "performances": "performance", "performed": "performance", "performing": "performance",
    "effects": "effect", "effective": "effect", "effectively": "effect",
    "effectiveness": "effect",
    "developments": "development", "developing": "development", "developed": "development",
    "differences": "difference", "different": "difference", "differently": "difference",
    "groups": "group", "grouped": "group", "grouping": "group",
    "practices": "practice", "practiced": "practice", "practicing": "practice",
    "practical": "practice",
    "competences": "competence", "competencies": "competence",
    "competency": "competence", "competent": "competence",
    "problems": "problem", "problematic": "problem",
    "contexts": "context", "contextual": "context",
    "countries": "country", "fields": "field", "papers": "paper",
    "orders": "order", "ordered": "order", "ordering": "order",
    "companies": "company",
    "works": "work", "worked": "work", "working": "work",
    "workers": "work", "worker": "work", "workplace": "work", "workplaces": "work",
    "learned": "learning", "learns": "learning",
}


# ── Text pre-processing ─────────────────────────────────────────────────────
def preprocess(text: str) -> list[str]:
    """Lowercase, tokenize, apply thesaurus, detect 'higher education' bigram."""
    text = text.lower()
    # Replace "higher education" bigram before tokenizing
    text = text.replace("higher education", "higher_education")
    tokens = re.findall(r"[a-z_]+", text)
    result = []
    for tok in tokens:
        tok = tok.replace("higher_education", "higher education")
        tok = THESAURUS.get(tok, tok)
        result.append(tok)
    return result


def build_cooccurrence_matrix(
    df: pd.DataFrame, keywords: list[str]
) -> np.ndarray:
    """Build a symmetric co-occurrence matrix from TI+AB fields.

    Uses binary counting: each document contributes at most 1 to each
    keyword pair.
    """
    kw_set = set(keywords)
    n = len(keywords)
    kw_index = {kw: i for i, kw in enumerate(keywords)}
    cooc = np.zeros((n, n), dtype=int)

    for _, row in df.iterrows():
        ti = str(row.get("TI", ""))
        ab = str(row.get("AB", ""))
        tokens = preprocess(ti + " " + ab)
        # Binary: which of the 28 keywords appear in this document?
        present = kw_set.intersection(tokens)
        present_list = sorted(present)
        for i_idx, kw_a in enumerate(present_list):
            for kw_b in present_list[i_idx:]:
                a = kw_index[kw_a]
                b = kw_index[kw_b]
                cooc[a][b] += 1
                if a != b:
                    cooc[b][a] += 1

    return cooc


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    setup_matplotlib()

    # Load data
    df_wos = load_savedrecs()
    df_map = load_vosviewer_map()

    keywords = df_map["label"].tolist()
    vos_clusters = df_map.set_index("label")["cluster"].to_dict()

    print(f"WoS records: {len(df_wos)}")
    print(f"VOSViewer keywords: {len(keywords)}")
    print()

    # ── 1. Build co-occurrence matrix ────────────────────────────────────────
    cooc = build_cooccurrence_matrix(df_wos, keywords)
    print("Co-occurrence matrix built (28×28)")
    print(f"  Non-zero off-diagonal pairs: {np.count_nonzero(np.triu(cooc, k=1))}")
    print()

    # ── 2. Build networkx graph ──────────────────────────────────────────────
    G = nx.Graph()
    G.add_nodes_from(keywords)
    n = len(keywords)
    for i in range(n):
        for j in range(i + 1, n):
            w = cooc[i][j]
            if w > 0:
                G.add_edge(keywords[i], keywords[j], weight=w)

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print()

    # ── 3. Sweep resolution parameter (fine step) ───────────────────────────
    vos_labels = [vos_clusters[kw] for kw in keywords]
    results = []

    for r100 in range(50, 201):  # 0.50 to 2.00, step 0.01
        r = r100 / 100.0
        partition = community.best_partition(G, resolution=r, random_state=42)
        n_clusters = len(set(partition.values()))
        results.append((r, n_clusters, partition))

    # Evaluate ARI for all solutions with 3-5 clusters
    candidates = []
    for r, nc, partition in results:
        if 3 <= nc <= 5:
            py_labs = [partition[kw] for kw in keywords]
            ari = adjusted_rand_score(vos_labels, py_labs)
            # Reject degenerate partitions (any cluster has < 2 members)
            sizes = pd.Series(list(partition.values())).value_counts()
            if sizes.min() >= 2:
                candidates.append((r, nc, partition, ari))

    if not candidates:
        # Accept even degenerate partitions as fallback
        for r, nc, partition in results:
            if 2 <= nc <= 6:
                py_labs = [partition[kw] for kw in keywords]
                ari = adjusted_rand_score(vos_labels, py_labs)
                candidates.append((r, nc, partition, ari))

    # Pick best ARI; prefer 4 clusters if ARI is within 0.05 of best
    candidates.sort(key=lambda x: x[3], reverse=True)
    best_r, best_nc, best_partition, best_ari = candidates[0]
    for r, nc, partition, ari in candidates:
        if nc == 4 and ari >= best_ari - 0.05:
            best_r, best_nc, best_partition, best_ari = r, nc, partition, ari
            break

    print(f"Best resolution: {best_r:.2f} ({best_nc} clusters, ARI={best_ari:.4f})")

    py_labels = [best_partition[kw] for kw in keywords]
    print()

    # ── 4. Print cluster assignments ─────────────────────────────────────────
    # Group keywords by Python cluster
    py_cluster_groups: dict[int, list[str]] = {}
    for kw, cl in best_partition.items():
        py_cluster_groups.setdefault(cl, []).append(kw)

    print("=" * 60)
    print("Python (Louvain) cluster assignments:")
    print("=" * 60)
    for cl_id in sorted(py_cluster_groups):
        members = sorted(py_cluster_groups[cl_id])
        print(f"\n  Cluster {cl_id} ({len(members)} keywords):")
        for kw in members:
            vos_cl = vos_clusters[kw]
            print(f"    {kw:<22s}  (VOSViewer cluster {vos_cl})")

    print()
    print("=" * 60)
    print("Comparison metrics:")
    print("=" * 60)

    ari = adjusted_rand_score(vos_labels, py_labels)
    nmi = normalized_mutual_info_score(vos_labels, py_labels)
    print(f"  ARI (Adjusted Rand Index):          {ari:.4f}")
    print(f"  NMI (Normalized Mutual Information): {nmi:.4f}")
    print()

    # ── Confusion matrix ─────────────────────────────────────────────────────
    vos_unique = sorted(set(vos_labels))
    py_unique = sorted(set(py_labels))
    # Build confusion matrix as DataFrame for clear display
    cm_df = pd.DataFrame(0, index=vos_unique, columns=py_unique)
    for kw, vos_cl, py_cl in zip(keywords, vos_labels, py_labels):
        cm_df.loc[vos_cl, py_cl] += 1

    print("Confusion matrix (rows=VOSViewer, cols=Python):")
    print()
    header = "VOSViewer\\Python  " + "  ".join(f"Cl.{c}" for c in py_unique)
    print(f"  {header}")
    print(f"  {'─' * len(header)}")
    for vos_cl in vos_unique:
        row_vals = "     ".join(f"{cm_df.loc[vos_cl, pc]:>3d}" for pc in py_unique)
        print(f"  Cluster {vos_cl}:         {row_vals}")
    print()

    # ── 5. Visualization ─────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 6))

    cm_array = cm_df.values.astype(int)
    im = ax.imshow(cm_array, cmap="YlOrRd", aspect="auto")

    # Axis labels
    ax.set_xticks(range(len(py_unique)))
    ax.set_xticklabels([f"Python {c}" for c in py_unique])
    ax.set_yticks(range(len(vos_unique)))
    ax.set_yticklabels([f"VOSViewer {c}" for c in vos_unique])

    ax.set_xlabel("Кластер Python (Louvain)")
    ax.set_ylabel("Кластер VOSViewer")
    ax.set_title("Порівняння кластерів: Python (Louvain) vs VOSViewer")

    # Annotate cells with counts
    for i in range(len(vos_unique)):
        for j in range(len(py_unique)):
            val = cm_array[i, j]
            color = "white" if val > cm_array.max() / 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color)

    plt.colorbar(im, ax=ax, label="Кількість ключових слів")
    fig.tight_layout()

    outpath = MEDIA_DIR / "fig_cluster_comparison.pdf"
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {outpath}")


if __name__ == "__main__":
    main()
