"""
Temporal and citation overlay maps for VOSViewer keyword network.

Produces three figures:
  1. fig_overlay_year.png        — node colour = avg publication year (viridis)
  2. fig_overlay_citations.png   — node colour = avg citations (coolwarm)
  3. fig_overlay_norm_citations.png — node colour = avg norm citations (RdYlGn)

Co-occurrence edges are computed inline from the merged WoS dataset
(TI + AB, binary counting, thesaurus normalisation).
"""

from __future__ import annotations

import re
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from wos_parser import load_savedrecs, load_vosviewer_map, MEDIA_DIR, setup_matplotlib

# ── Thesaurus for term normalisation ─────────────────────────────────────────
THESAURUS: dict[str, str] = {
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


def _tokenize_and_normalize(text: str, keywords: set[str]) -> set[str]:
    """Tokenize text, apply thesaurus, detect bigrams, return matched keywords."""
    text = text.lower()

    # Detect "higher education" bigram before splitting
    found: set[str] = set()
    if "higher education" in text:
        found.add("higher education")

    tokens = re.findall(r"[a-z]+", text)
    normalised = [THESAURUS.get(tok, tok) for tok in tokens]

    for tok in normalised:
        if tok in keywords:
            found.add(tok)

    return found


def build_cooccurrence_matrix(
    df_wos: pd.DataFrame,
    keywords: list[str],
) -> np.ndarray:
    """Build a symmetric co-occurrence matrix (binary counting per record).

    Combines TI (title) and AB (abstract) fields.  Each record contributes
    at most 1 to each keyword-pair cell.
    """
    kw_set = set(keywords)
    kw_index = {kw: i for i, kw in enumerate(keywords)}
    n = len(keywords)
    matrix = np.zeros((n, n), dtype=int)

    for _, row in df_wos.iterrows():
        title = str(row.get("TI", ""))
        abstract = str(row.get("AB", ""))
        text = title + " " + abstract

        present = _tokenize_and_normalize(text, kw_set)
        present_list = sorted(present)  # deterministic order

        for kw_a, kw_b in combinations(present_list, 2):
            i, j = kw_index[kw_a], kw_index[kw_b]
            matrix[i, j] += 1
            matrix[j, i] += 1

    return matrix


def _draw_edges(
    ax: plt.Axes,
    cooc: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
) -> None:
    """Draw light-gray edges for non-zero co-occurrence pairs."""
    n = cooc.shape[0]
    # Normalise line width by max co-occurrence
    max_cooc = cooc.max() if cooc.max() > 0 else 1
    for i in range(n):
        for j in range(i + 1, n):
            if cooc[i, j] > 0:
                weight = cooc[i, j] / max_cooc
                ax.plot(
                    [xs[i], xs[j]],
                    [ys[i], ys[j]],
                    color="lightgray",
                    alpha=0.1 + 0.2 * weight,
                    linewidth=0.3 + 0.7 * weight,
                    zorder=1,
                )


def _draw_overlay(
    df_map: pd.DataFrame,
    cooc: np.ndarray,
    color_col: str,
    cmap: str,
    cbar_label: str,
    title: str,
    outfile: str,
    node_scale: float = 15.0,
) -> None:
    """Draw a single overlay map and save to *outfile*."""
    fig, ax = plt.subplots(figsize=(14, 10))

    xs = df_map["x"].values
    ys = df_map["y"].values
    labels = df_map["label"].values
    sizes = np.sqrt(df_map["occurrences"].values) * node_scale
    values = df_map[color_col].values

    # Draw edges first (behind nodes)
    _draw_edges(ax, cooc, xs, ys)

    # Scatter nodes
    norm = Normalize(vmin=values.min(), vmax=values.max())
    sc = ax.scatter(
        xs,
        ys,
        c=values,
        cmap=cmap,
        s=sizes,
        edgecolors="black",
        linewidths=0.5,
        zorder=5,
        norm=norm,
    )

    # Colorbar
    cbar = fig.colorbar(sc, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label(cbar_label, fontsize=12)

    # Labels
    for i, lbl in enumerate(labels):
        ax.annotate(
            lbl,
            (xs[i], ys[i]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
            zorder=10,
            ha="left",
            va="bottom",
            bbox=dict(
                boxstyle="round,pad=0.15",
                facecolor="white",
                edgecolor="none",
                alpha=0.7,
            ),
        )

    ax.set_title(title, fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("x (VOSViewer)")
    ax.set_ylabel("y (VOSViewer)")
    ax.grid(True, linestyle="--", alpha=0.25)

    fig.tight_layout()
    outpath = MEDIA_DIR / outfile
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {outpath}")


def main() -> None:
    setup_matplotlib()

    print("Loading VOSViewer keyword map …")
    df_map = load_vosviewer_map()
    keywords = df_map["label"].tolist()
    print(f"  {len(keywords)} keywords")

    print("Loading WoS records (savedrecs.txt) …")
    df_wos = load_savedrecs()
    print(f"  {len(df_wos)} records")

    print("Building co-occurrence matrix …")
    cooc = build_cooccurrence_matrix(df_wos, keywords)
    nonzero_pairs = (cooc > 0).sum() // 2
    print(f"  {nonzero_pairs} non-zero keyword pairs")

    # ── 1. Temporal overlay ──────────────────────────────────────────────────
    print("1/3  Temporal overlay (avg pub year) …")
    _draw_overlay(
        df_map,
        cooc,
        color_col="avg_pub_year",
        cmap="viridis",
        cbar_label="Середній рік публікації",
        title="Часова карта ключових слів",
        outfile="fig_overlay_year.png",
    )

    # ── 2. Citation overlay ──────────────────────────────────────────────────
    print("2/3  Citation overlay (avg citations) …")
    _draw_overlay(
        df_map,
        cooc,
        color_col="avg_citations",
        cmap="coolwarm",
        cbar_label="Середня кількість цитувань",
        title="Карта цитованості ключових слів",
        outfile="fig_overlay_citations.png",
    )

    # ── 3. Normalized citation overlay ───────────────────────────────────────
    print("3/3  Normalized citation overlay (avg norm citations) …")
    _draw_overlay(
        df_map,
        cooc,
        color_col="avg_norm_citations",
        cmap="RdYlGn",
        cbar_label="Середня нормалізована цитованість",
        title="Карта нормалізованої цитованості",
        outfile="fig_overlay_norm_citations.png",
    )

    print("Done.")


if __name__ == "__main__":
    main()
