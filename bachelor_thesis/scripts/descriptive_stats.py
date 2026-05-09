"""
Descriptive statistics of the bibliometric dataset (Web of Science export).

Produces seven charts saved to media/ and prints a summary to stdout.
Imports shared helpers from wos_parser.py in the same directory.
"""

import re
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

from wos_parser import MEDIA_DIR, load_merged, setup_matplotlib

# ── Configuration ────────────────────────────────────────────────────────────
BAR_COLOR = "#4C72B0"
BAR_COLOR_ALT = "#55A868"
BAR_COLOR_KW = "#C44E52"
BAR_COLOR_KW2 = "#8172B2"


def _field_coverage(df: pd.DataFrame, fields: list[str]) -> dict[str, float]:
    """Return percentage of non-null, non-empty values for each field."""
    coverage = {}
    for f in fields:
        if f in df.columns:
            non_null = df[f].dropna().astype(str).str.strip().replace("", pd.NA).dropna()
            coverage[f] = len(non_null) / len(df) * 100
        else:
            coverage[f] = 0.0
    return coverage


# ── 1. Publication year distribution ─────────────────────────────────────────
def plot_pub_years(df: pd.DataFrame) -> None:
    """Bar chart of publication counts by year (PY field)."""
    years = df["PY"].dropna().astype(int)
    year_counts = years.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(year_counts.index.astype(str), year_counts.values, color=BAR_COLOR, edgecolor="white")
    ax.set_title("Розподіл публікацій за роками", fontsize=14, fontweight="bold")
    ax.set_xlabel("Рік")
    ax.set_ylabel("Кількість публікацій")
    ax.tick_params(axis="x", rotation=60, labelsize=9)

    # Add value labels on top of bars
    for x_pos, (_, val) in enumerate(year_counts.items()):
        if val >= 5:
            ax.text(x_pos, val + 0.5, str(val), ha="center", va="bottom", fontsize=7)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_pub_years.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [1/7] fig_pub_years.png — {len(year_counts)} unique years, range {years.min()}–{years.max()}")


# ── 2. Document types ────────────────────────────────────────────────────────
def plot_doc_types(df: pd.DataFrame) -> None:
    """Bar chart of document types (DT field)."""
    dt = df["DT"].dropna().str.strip()
    dt_counts = dt.value_counts()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(dt_counts.index[::-1], dt_counts.values[::-1], color=BAR_COLOR_ALT, edgecolor="white")
    ax.set_title("Типи документів", fontsize=14, fontweight="bold")
    ax.set_xlabel("Кількість")

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                str(int(width)), ha="left", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_doc_types.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [2/7] fig_doc_types.png — {len(dt_counts)} document types")


# ── 3. Top 15 sources ───────────────────────────────────────────────────────
def plot_top_sources(df: pd.DataFrame, top_n: int = 15) -> None:
    """Horizontal bar chart of top journals/conferences (SO field)."""
    so = df["SO"].dropna().str.strip()
    so_counts = so.value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 7))
    # Reverse so the most frequent is at the top
    ax.barh(so_counts.index[::-1], so_counts.values[::-1], color=BAR_COLOR, edgecolor="white")
    ax.set_title("Топ-15 джерел", fontsize=14, fontweight="bold")
    ax.set_xlabel("Кількість публікацій")

    # Truncate long source names for readability
    labels = [s if len(s) <= 60 else s[:57] + "..." for s in so_counts.index[::-1]]
    ax.set_yticklabels(labels, fontsize=9)

    # Add value labels
    for i, val in enumerate(so_counts.values[::-1]):
        ax.text(val + 0.3, i, str(val), ha="left", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_top_sources.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [3/7] fig_top_sources.png — top {top_n} of {so.nunique()} unique sources")


# ── 4. Top 20 authors ───────────────────────────────────────────────────────
def plot_top_authors(df: pd.DataFrame, top_n: int = 20) -> None:
    """Horizontal bar chart of most prolific authors (AU field, semicolon-separated)."""
    author_counter: Counter = Counter()
    for au_str in df["AU"].dropna():
        authors = [a.strip() for a in au_str.split(";") if a.strip()]
        author_counter.update(authors)

    top_authors = author_counter.most_common(top_n)
    names = [a[0] for a in top_authors]
    counts = [a[1] for a in top_authors]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(names[::-1], counts[::-1], color=BAR_COLOR_ALT, edgecolor="white")
    ax.set_title("Топ-20 авторів", fontsize=14, fontweight="bold")
    ax.set_xlabel("Кількість публікацій")
    ax.tick_params(axis="y", labelsize=9)

    for i, val in enumerate(counts[::-1]):
        ax.text(val + 0.1, i, str(val), ha="left", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_top_authors.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [4/7] fig_top_authors.png — top {top_n} of {len(author_counter)} unique authors")


# ── 5. Top 20 countries ─────────────────────────────────────────────────────
def _extract_countries(c1_series: pd.Series) -> Counter:
    """Extract countries from C1 (affiliation) field.

    C1 format example:
        [Author, A] Univ Example, City, Country; [Author, B] Another Univ, Town, Country2
    Country is the text after the last comma inside each bracketed group, or
    the last comma-separated token of each semicolon-separated affiliation.
    """
    country_counter: Counter = Counter()
    bracket_pattern = re.compile(r"\[.*?\]\s*(.*?)(?=;\s*\[|$)")

    for c1_str in c1_series.dropna():
        # Try bracketed affiliations first
        affiliations = bracket_pattern.findall(c1_str)
        if not affiliations:
            # Fallback: split by semicolon
            affiliations = [seg.strip() for seg in c1_str.split(";") if seg.strip()]

        for aff in affiliations:
            parts = [p.strip() for p in aff.split(",")]
            if parts:
                country = parts[-1].strip().rstrip(".")
                if country:
                    country_counter[country] += 1

    return country_counter


def plot_top_countries(df: pd.DataFrame, top_n: int = 20) -> None:
    """Horizontal bar chart of top countries by affiliation count (C1 field)."""
    country_counter = _extract_countries(df["C1"])
    top_countries = country_counter.most_common(top_n)
    names = [c[0] for c in top_countries]
    counts = [c[1] for c in top_countries]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(names[::-1], counts[::-1], color=BAR_COLOR, edgecolor="white")
    ax.set_title("Топ-20 країн", fontsize=14, fontweight="bold")
    ax.set_xlabel("Кількість афіліацій")
    ax.tick_params(axis="y", labelsize=9)

    for i, val in enumerate(counts[::-1]):
        ax.text(val + 0.3, i, str(val), ha="left", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_top_countries.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [5/7] fig_top_countries.png — top {top_n} of {len(country_counter)} unique countries")


# ── 6. Top 30 author keywords (DE) ──────────────────────────────────────────
def _split_keywords(series: pd.Series) -> Counter:
    """Split semicolon-separated keyword field, lowercase, and count."""
    kw_counter: Counter = Counter()
    for kw_str in series.dropna():
        keywords = [k.strip().lower() for k in kw_str.split(";") if k.strip()]
        kw_counter.update(keywords)
    return kw_counter


def plot_keywords_de(df: pd.DataFrame, top_n: int = 30) -> None:
    """Horizontal bar chart of top author keywords (DE field)."""
    kw_counter = _split_keywords(df["DE"])
    top_kw = kw_counter.most_common(top_n)
    labels = [k[0] for k in top_kw]
    counts = [k[1] for k in top_kw]

    fig, ax = plt.subplots(figsize=(12, 9))
    ax.barh(labels[::-1], counts[::-1], color=BAR_COLOR_KW, edgecolor="white")
    ax.set_title("Топ-30 авторських ключових слів (DE)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Кількість")
    ax.tick_params(axis="y", labelsize=8)

    for i, val in enumerate(counts[::-1]):
        ax.text(val + 0.2, i, str(val), ha="left", va="center", fontsize=8)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_keywords_de.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [6/7] fig_keywords_de.png — top {top_n} of {len(kw_counter)} unique author keywords")


# ── 7. Top 30 Keywords Plus (ID) ────────────────────────────────────────────
def plot_keywords_id(df: pd.DataFrame, top_n: int = 30) -> None:
    """Horizontal bar chart of top Keywords Plus (ID field)."""
    kw_counter = _split_keywords(df["ID"])
    top_kw = kw_counter.most_common(top_n)
    labels = [k[0] for k in top_kw]
    counts = [k[1] for k in top_kw]

    fig, ax = plt.subplots(figsize=(12, 9))
    ax.barh(labels[::-1], counts[::-1], color=BAR_COLOR_KW2, edgecolor="white")
    ax.set_title("Топ-30 Keywords Plus (ID)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Кількість")
    ax.tick_params(axis="y", labelsize=8)

    for i, val in enumerate(counts[::-1]):
        ax.text(val + 0.2, i, str(val), ha="left", va="center", fontsize=8)

    plt.tight_layout()
    plt.savefig(MEDIA_DIR / "fig_keywords_id.pdf", bbox_inches="tight")
    plt.close()
    print(f"  [7/7] fig_keywords_id.png — top {top_n} of {len(kw_counter)} unique Keywords Plus")


# ── Summary ──────────────────────────────────────────────────────────────────
def print_summary(df: pd.DataFrame) -> None:
    """Print descriptive summary to stdout."""
    n = len(df)
    years = df["PY"].dropna().astype(int)

    print("=" * 65)
    print("  ОПИСОВА СТАТИСТИКА БІБЛІОМЕТРИЧНОГО ДАТАСЕТУ")
    print("=" * 65)
    print(f"  Всього записів:        {n}")
    print(f"  Діапазон років:        {years.min()} – {years.max()}")
    print(f"  Медіана року:          {int(years.median())}")
    print(f"  Середній рік:          {years.mean():.1f}")
    print()

    key_fields = ["AU", "TI", "SO", "PY", "DT", "DE", "ID", "C1", "AB", "CR"]
    coverage = _field_coverage(df, key_fields)
    print("  Покриття полів (% непустих):")
    for field, pct in coverage.items():
        bar = "#" * int(pct / 2)
        print(f"    {field:4s}  {pct:5.1f}%  {bar}")
    print("=" * 65)


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    setup_matplotlib()

    # Try to use seaborn-style grid; fall back gracefully
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        try:
            plt.style.use("seaborn-whitegrid")
        except OSError:
            pass  # use default style

    print("Завантаження merged_data.txt ...")
    df = load_merged()
    print(f"Завантажено {len(df)} записів.\n")

    print_summary(df)
    print("\nГенерація графіків ...\n")

    plot_pub_years(df)
    plot_doc_types(df)
    plot_top_sources(df)
    plot_top_authors(df)
    plot_top_countries(df)
    plot_keywords_de(df)
    plot_keywords_id(df)

    print(f"\nУсі графіки збережено до: {MEDIA_DIR}/")


if __name__ == "__main__":
    main()
