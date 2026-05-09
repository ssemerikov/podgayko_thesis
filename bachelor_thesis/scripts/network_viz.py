"""
Network visualizations of keyword co-occurrence from WoS titles and abstracts.

Produces three figures:
1. fig_network_vosviewer.png  — VOSViewer coordinate layout
2. fig_network_python.png     — Fruchterman-Reingold + Louvain clustering
3. fig_network_comparison.png — side-by-side comparison

Co-occurrence matrix: binary counting over TI+AB for the 28 VOSViewer keywords,
with thesaurus normalization (VET variants, student variants) and bigram detection
("higher education").
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from community import community_louvain          # python-louvain
from sklearn.metrics import adjusted_rand_score

# Import from shared parser in the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
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

# Known multi-word VOSViewer terms
MULTIWORD_TERMS = {
    ("higher", "education"): "higher education",
}

# ── Cluster colour palette ───────────────────────────────────────────────────
CLUSTER_COLORS = {
    1: "#e41a1c",   # red
    2: "#4daf4a",   # green
    3: "#377eb8",   # blue
    4: "#ff7f00",   # orange
}


# ══════════════════════════════════════════════════════════════════════════════
#  Tokenization & co-occurrence
# ══════════════════════════════════════════════════════════════════════════════

def tokenize_document(text: str) -> set[str]:
    """Tokenize text into a set of unique terms with thesaurus + bigram handling."""
    words = re.findall(r"\b[a-z]{2,}\b", text.lower())
    word_set = set(words)

    # Detect multi-word terms
    consumed: set[str] = set()
    multiword_found: set[str] = set()
    for (w1, w2), term in MULTIWORD_TERMS.items():
        if w1 in word_set and w2 in word_set:
            multiword_found.add(term)
            consumed.add(w1)

    # Apply thesaurus
    final: set[str] = set()
    for w in word_set:
        if w in consumed:
            continue
        final.add(THESAURUS.get(w, w))

    final |= multiword_found
    return final


def build_cooccurrence_matrix(
    df: pd.DataFrame, keywords: list[str]
) -> np.ndarray:
    """Build a symmetric co-occurrence matrix for *keywords* across TI+AB.

    Binary counting: each keyword counted at most once per document.
    Returns an (n, n) symmetric numpy array.
    """
    kw_set = set(keywords)
    kw_index = {kw: i for i, kw in enumerate(keywords)}
    n = len(keywords)
    matrix = np.zeros((n, n), dtype=int)

    for _, row in df.iterrows():
        title = str(row.get("TI", "")) if pd.notna(row.get("TI")) else ""
        abstract = str(row.get("AB", "")) if pd.notna(row.get("AB")) else ""
        terms = tokenize_document(title + " " + abstract)

        # Keep only target keywords found in this document
        present = sorted(terms & kw_set)
        for i_idx in range(len(present)):
            for j_idx in range(i_idx + 1, len(present)):
                a = kw_index[present[i_idx]]
                b = kw_index[present[j_idx]]
                matrix[a, b] += 1
                matrix[b, a] += 1

    return matrix


def build_graph(keywords: list[str], cooc: np.ndarray,
                occurrences: dict[str, int]) -> nx.Graph:
    """Build a networkx Graph from the co-occurrence matrix."""
    G = nx.Graph()
    n = len(keywords)
    for i in range(n):
        G.add_node(keywords[i], occurrences=occurrences.get(keywords[i], 1))
    for i in range(n):
        for j in range(i + 1, n):
            if cooc[i, j] > 0:
                G.add_edge(keywords[i], keywords[j], weight=cooc[i, j])
    return G


# ══════════════════════════════════════════════════════════════════════════════
#  Louvain clustering with best-match colour mapping
# ══════════════════════════════════════════════════════════════════════════════

def louvain_clusters(G: nx.Graph, resolution: float = 1.0,
                     seed: int = 42) -> dict[str, int]:
    """Run Louvain and return node → cluster_id (1-based)."""
    partition = community_louvain.best_partition(
        G, weight="weight", resolution=resolution, random_state=seed,
    )
    # Relabel to 1-based
    unique = sorted(set(partition.values()))
    remap = {old: new + 1 for new, old in enumerate(unique)}
    return {node: remap[cid] for node, cid in partition.items()}


def match_cluster_colors(
    vos_clusters: dict[str, int],
    py_clusters: dict[str, int],
) -> dict[int, str]:
    """Map Python cluster IDs to colours that best match VOSViewer clusters.

    Uses overlap counting: for each (py_cluster, vos_cluster) pair, count
    shared nodes.  Greedily assign colours to maximise total overlap.
    """
    from itertools import permutations

    py_ids = sorted(set(py_clusters.values()))
    vos_ids = sorted(set(vos_clusters.values()))

    # Build overlap matrix
    overlap = {}
    for pid in py_ids:
        py_nodes = {n for n, c in py_clusters.items() if c == pid}
        for vid in vos_ids:
            vos_nodes = {n for n, c in vos_clusters.items() if c == vid}
            overlap[(pid, vid)] = len(py_nodes & vos_nodes)

    # Try all permutations of vos_ids assignment to py_ids (at most 4! = 24)
    best_score = -1
    best_mapping: dict[int, int] = {}
    for perm in permutations(vos_ids):
        score = sum(overlap.get((pid, vid), 0)
                    for pid, vid in zip(py_ids, perm))
        if score > best_score:
            best_score = score
            best_mapping = dict(zip(py_ids, perm))

    # Map python cluster id → colour (via matched VOSViewer cluster)
    return {pid: CLUSTER_COLORS[best_mapping.get(pid, 1)] for pid in py_ids}


# ══════════════════════════════════════════════════════════════════════════════
#  Drawing helpers
# ══════════════════════════════════════════════════════════════════════════════

def _edge_data(G: nx.Graph, top_n: int | None = 50):
    """Return edge list, widths, and alphas for drawing.

    If top_n is given, keep only the top_n edges by weight.
    Widths and alphas are normalized by max weight.
    """
    edges = sorted(G.edges(data=True), key=lambda e: e[2]["weight"], reverse=True)
    if top_n is not None and len(edges) > top_n:
        edges = edges[:top_n]

    if not edges:
        return [], [], []

    max_w = edges[0][2]["weight"]
    edge_list = [(u, v) for u, v, _ in edges]
    widths = [e[2]["weight"] / max_w * 3.0 for e in edges]
    alphas = [0.15 + 0.60 * (e[2]["weight"] / max_w) for e in edges]
    return edge_list, widths, alphas


def draw_network(
    ax: matplotlib.axes.Axes,
    G: nx.Graph,
    pos: dict[str, tuple[float, float]],
    node_colors: list[str],
    node_sizes: list[float],
    title: str,
    top_edges: int | None = 50,
):
    """Draw a keyword co-occurrence network on the given axes."""
    edge_list, widths, alphas = _edge_data(G, top_n=top_edges)

    # Draw edges one-by-one to support per-edge alpha
    for (u, v), w, a in zip(edge_list, widths, alphas):
        nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)], width=w, alpha=a,
            edge_color="#888888", ax=ax,
        )

    nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes, node_color=node_colors,
        edgecolors="white", linewidths=0.5, ax=ax,
    )

    # Labels at node centres
    nx.draw_networkx_labels(
        G, pos, font_size=7, font_weight="bold", ax=ax,
    )

    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.axis("off")


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    setup_matplotlib()

    # ── Load data ─────────────────────────────────────────────────────────────
    print("Loading WoS records...")
    df_wos = load_savedrecs()
    print(f"  {len(df_wos)} records")

    print("Loading VOSViewer keyword map...")
    df_vos = load_vosviewer_map()
    keywords = df_vos["label"].str.lower().tolist()
    print(f"  {len(keywords)} keywords: {keywords[:5]}...")

    # Occurrence lookup
    occ = dict(zip(df_vos["label"].str.lower(), df_vos["occurrences"]))

    # VOSViewer cluster lookup
    vos_clusters = dict(zip(df_vos["label"].str.lower(), df_vos["cluster"]))

    # VOSViewer x, y coordinates
    vos_pos = dict(zip(
        df_vos["label"].str.lower(),
        zip(df_vos["x"], df_vos["y"]),
    ))

    # ── Build co-occurrence matrix ────────────────────────────────────────────
    print("Building co-occurrence matrix...")
    cooc = build_cooccurrence_matrix(df_wos, keywords)
    total_pairs = (cooc > 0).sum() // 2
    print(f"  Non-zero pairs: {total_pairs}")

    # ── Build graph ───────────────────────────────────────────────────────────
    G = build_graph(keywords, cooc, occ)
    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # ── Node sizes (sqrt of occurrences, scaled) ─────────────────────────────
    scaling_factor = 80
    node_sizes = [np.sqrt(occ.get(n, 1)) * scaling_factor for n in G.nodes()]

    # ── VOSViewer cluster colours ─────────────────────────────────────────────
    vos_node_colors = [CLUSTER_COLORS.get(vos_clusters.get(n, 1), "#999999")
                       for n in G.nodes()]

    # ── Python Louvain clustering (sweep resolution, best ARI) ───────────────
    print("Running Louvain community detection (resolution sweep)...")
    nodes_ordered = list(G.nodes())
    vos_labels = [vos_clusters.get(n, 0) for n in nodes_ordered]
    best_ari = -1.0
    best_res = 1.0
    best_partition = None
    for r100 in range(50, 201):  # 0.50 to 2.00, step 0.01
        r = r100 / 100.0
        part = louvain_clusters(G, resolution=r, seed=42)
        nc = len(set(part.values()))
        if 3 <= nc <= 5:
            # Reject degenerate partitions (singleton clusters)
            sizes = [sum(1 for v in part.values() if v == c) for c in set(part.values())]
            if min(sizes) < 2:
                continue
            py_lab = [part.get(n, 0) for n in nodes_ordered]
            ari_val = adjusted_rand_score(vos_labels, py_lab)
            if ari_val > best_ari:
                best_ari = ari_val
                best_res = r
                best_partition = part
    if best_partition is None:
        best_partition = louvain_clusters(G, resolution=1.0, seed=42)
        best_ari = adjusted_rand_score(
            vos_labels, [best_partition.get(n, 0) for n in nodes_ordered])
        best_res = 1.0
    py_clusters = best_partition
    n_py_clusters = len(set(py_clusters.values()))
    ari = best_ari
    print(f"  Best resolution: {best_res}, {n_py_clusters} clusters, ARI={ari:.4f}")

    # Map Louvain colours to best-match VOSViewer colours
    py_color_map = match_cluster_colors(vos_clusters, py_clusters)
    py_node_colors = [py_color_map.get(py_clusters.get(n, 1), "#999999")
                      for n in G.nodes()]

    # ── Spring layout ─────────────────────────────────────────────────────────
    spring_pos = nx.spring_layout(G, weight="weight", seed=42)

    # ══════════════════════════════════════════════════════════════════════════
    #  Figure 1: VOSViewer coordinate layout
    # ══════════════════════════════════════════════════════════════════════════
    print("\nDrawing fig_network_vosviewer.png...")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    draw_network(
        ax1, G, vos_pos, vos_node_colors, node_sizes,
        title="Мережа ключових слів (координати VOSViewer)",
    )
    fig1.tight_layout()
    path1 = MEDIA_DIR / "fig_network_vosviewer.pdf"
    fig1.savefig(path1, bbox_inches="tight")
    plt.close(fig1)
    print(f"  Saved: {path1}")

    # ══════════════════════════════════════════════════════════════════════════
    #  Figure 2: Fruchterman-Reingold + Louvain
    # ══════════════════════════════════════════════════════════════════════════
    print("Drawing fig_network_python.png...")
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    draw_network(
        ax2, G, spring_pos, py_node_colors, node_sizes,
        title="Мережа ключових слів (Fruchterman-Reingold, Louvain)",
    )
    fig2.tight_layout()
    path2 = MEDIA_DIR / "fig_network_python.pdf"
    fig2.savefig(path2, bbox_inches="tight")
    plt.close(fig2)
    print(f"  Saved: {path2}")

    # ══════════════════════════════════════════════════════════════════════════
    #  Figure 3: Side-by-side comparison
    # ══════════════════════════════════════════════════════════════════════════
    print("Drawing fig_network_comparison.png...")
    fig3, (ax3l, ax3r) = plt.subplots(1, 2, figsize=(18, 8))
    draw_network(
        ax3l, G, vos_pos, vos_node_colors, node_sizes,
        title="VOSViewer (оригінальні координати)",
    )
    draw_network(
        ax3r, G, spring_pos, py_node_colors, node_sizes,
        title="Python (Fruchterman-Reingold, Louvain)",
    )
    fig3.suptitle("Порівняння мережевих візуалізацій",
                  fontsize=15, fontweight="bold", y=0.98)
    fig3.tight_layout(rect=[0, 0, 1, 0.95])
    path3 = MEDIA_DIR / "fig_network_comparison.pdf"
    fig3.savefig(path3, bbox_inches="tight")
    plt.close(fig3)
    print(f"  Saved: {path3}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("CLUSTER COMPARISON")
    print("=" * 60)
    print(f"  {'Keyword':<25s} {'VOSViewer':>10s} {'Louvain':>10s}")
    print("  " + "-" * 47)
    for n in sorted(G.nodes()):
        vc = vos_clusters.get(n, "?")
        pc = py_clusters.get(n, "?")
        marker = " *" if vc != pc else ""
        print(f"  {n:<25s} {vc:>10} {pc:>10}{marker}")
    print(f"\n  ARI = {ari:.4f}")
    print(f"  (* = cluster mismatch between VOSViewer and Louvain)")
    print("\nDone.")


if __name__ == "__main__":
    main()
