"""
Shared parser for Web of Science plain-text exports and VOSViewer map data.
Used by all analysis scripts in this project.
"""

import re
from pathlib import Path

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# ── Path constants ────────────────────────────────────────────────────────────
# Layout: bachelor_thesis/scripts/wos_parser.py
#         bachelor_thesis/data_src/  → symlink to ../part1/Дані/
#         bachelor_thesis/data/      → derived artifacts (thesaurus, prior_reviews)
#         bachelor_thesis/media/     → figures consumed by main.tex
ROOT_DIR = Path(__file__).resolve().parent.parent  # bachelor_thesis/
DATA_DIR = ROOT_DIR / "data_src"                   # raw WoS exports + VOSViewer map
DERIVED_DIR = ROOT_DIR / "data"                    # thesaurus, prior_reviews, etc.
MEDIA_DIR = ROOT_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True)
DERIVED_DIR.mkdir(exist_ok=True)


# ── WoS plain-text parser ────────────────────────────────────────────────────
def parse_wos(filepath: str | Path) -> pd.DataFrame:
    """Parse a Web of Science plain-text export file into a DataFrame.

    Each record becomes a row. Multi-value fields (AU, C1, CR, etc.) are
    joined with '; '.  Continuation lines (starting with 3 spaces) are
    appended to the previous field.
    """
    filepath = Path(filepath)
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    current_tag: str | None = None

    with open(filepath, encoding="utf-8-sig") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n\r")

            # Skip file header / footer lines
            if line.startswith("FN ") or line.startswith("VR "):
                continue
            if line.startswith("EF"):
                break

            # End-of-record
            if line.strip() == "ER":
                if current:
                    records.append(current)
                current = {}
                current_tag = None
                continue

            # Continuation line (3 leading spaces)
            if line.startswith("   ") and current_tag:
                current[current_tag] += "; " + line.strip()
                continue

            # New field tag (first 2 chars)
            if len(line) >= 3 and line[2] == " ":
                tag = line[:2].strip()
                value = line[3:].strip()
                if tag:
                    current_tag = tag
                    if tag in current:
                        current[tag] += "; " + value
                    else:
                        current[tag] = value

    if current:  # last record if no trailing ER
        records.append(current)

    return pd.DataFrame(records)


# ── Convenience loaders ───────────────────────────────────────────────────────
def load_savedrecs() -> pd.DataFrame:
    """Load savedrecs.txt (1000 records, no DE/ID keywords)."""
    return parse_wos(DATA_DIR / "savedrecs.txt")


def load_merged() -> pd.DataFrame:
    """Load merged_data.txt (1998 records, full fields)."""
    return parse_wos(DATA_DIR / "merged_data.txt")


def load_vosviewer_map() -> pd.DataFrame:
    """Load VOSViewer keyword map (КлючовісловаКАРТА.txt)."""
    df = pd.read_csv(
        DATA_DIR / "КлючовісловаКАРТА.txt",
        sep="\t",
    )
    # Normalise column names
    df.columns = [
        "id", "label", "x", "y", "cluster",
        "links", "tls", "occurrences",
        "avg_pub_year", "avg_citations", "avg_norm_citations",
    ]
    return df


# ── Matplotlib setup ─────────────────────────────────────────────────────────
def setup_matplotlib():
    """Configure matplotlib for publication-quality vector figures with Ukrainian text.

    Per Положення КДПУ + supervisor remark: figures must be in vector formats
    (PDF/TikZ). All matplotlib outputs are saved as PDF; raster fallback only
    for inherently bitmap data (e.g. heatmaps with embedded color images).
    """
    matplotlib.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Tempora", "Liberation Serif", "DejaVu Serif"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.format": "pdf",
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,   # embed TrueType — ensures vector text
        "ps.fonttype": 42,
        "figure.figsize": (10, 6),
    })


# ── Self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    setup_matplotlib()

    df_vos = load_savedrecs()
    print(f"savedrecs.txt:  {len(df_vos)} records, columns: {list(df_vos.columns[:10])}...")

    df_full = load_merged()
    print(f"merged_data.txt: {len(df_full)} records, columns: {list(df_full.columns[:10])}...")

    df_map = load_vosviewer_map()
    print(f"VOSViewer map:   {len(df_map)} keywords")
    print(df_map[["label", "cluster", "occurrences", "tls"]].to_string(index=False))
