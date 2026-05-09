#!/usr/bin/env python3
"""
Build a keyword co-occurrence matrix from WoS title+abstract text mining
and compare the resulting metrics with VOSViewer link/TLS values.

Self-contained: replicates the text-mining pipeline inline so no dependency
on text_mining.py.  Imports only the shared parser helpers from wos_parser.

Usage:
    python scripts/cooccurrence.py
"""

import re
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from wos_parser import load_savedrecs, load_vosviewer_map, MEDIA_DIR, setup_matplotlib

# ── Thesaurus ────────────────────────────────────────────────────────────────
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

# ── Stopwords (~150 common English + domain excludes) ────────────────────────
STOPWORDS: set[str] = {
    "the", "of", "and", "to", "in", "is", "it", "for", "that", "was",
    "on", "are", "as", "with", "his", "they", "be", "at", "one", "have",
    "this", "from", "or", "had", "by", "not", "but", "what", "all", "were",
    "we", "when", "your", "can", "said", "there", "each", "which", "she",
    "do", "how", "their", "if", "will", "up", "other", "about", "out",
    "many", "then", "them", "these", "so", "some", "her", "would", "make",
    "like", "him", "into", "has", "two", "more", "no", "way", "could",
    "people", "my", "than", "first", "been", "who", "its", "now", "find",
    "long", "down", "day", "did", "get", "come", "made", "after", "back",
    "only", "me", "our", "under", "may", "between", "through", "where",
    "much", "before", "should", "well", "also", "any", "because", "does",
    "just", "over", "such", "both", "most", "very", "an", "own", "say",
    "he", "she", "it", "us", "am", "being", "those", "here", "during",
    "while", "above", "below", "few", "same", "again", "once", "further",
    "why", "how", "nor", "too", "off", "against", "until", "without",
    "among", "around", "however", "still", "might", "must", "shall",
    "since", "yet", "already", "often", "always", "never", "either",
    "neither", "per", "upon", "within", "across", "along", "toward",
    "towards", "whether", "though", "although", "rather", "quite",
    "enough", "less", "another", "else", "every", "even", "let", "put",
    "take", "went", "going", "using", "used", "based", "given", "thus",
    "hence", "therefore", "moreover", "furthermore", "nevertheless",
    "whereas", "whereby", "wherein", "et", "al", "ie", "eg",
    # domain excludes
    "article", "patient", "year",
}


# ── Text-mining helpers ──────────────────────────────────────────────────────

def _combine_text(row: pd.Series) -> str:
    """Concatenate title + abstract into a single lowercase string."""
    ti = str(row.get("TI", "")) if pd.notna(row.get("TI")) else ""
    ab = str(row.get("AB", "")) if pd.notna(row.get("AB")) else ""
    return (ti + " " + ab).lower()


def _tokenize(text: str) -> list[str]:
    """Extract lowercase alpha tokens of length >= 2."""
    return re.findall(r"\b[a-z]{2,}\b", text)


def _apply_thesaurus(tokens: list[str]) -> list[str]:
    """Map synonyms via THESAURUS; pass-through for unmapped tokens."""
    return [THESAURUS.get(tok, tok) for tok in tokens]


def _handle_bigrams(tokens: list[str]) -> list[str]:
    """Detect 'higher education' bigram and insert it as a single token."""
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and tokens[i] == "higher" and tokens[i + 1] == "education":
            out.append("higher education")
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out


def _remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove stopwords (but keep multi-word terms like 'higher education')."""
    return [t for t in tokens if t not in STOPWORDS or " " in t]


def extract_terms(text: str) -> set[str]:
    """Full pipeline: tokenize → thesaurus → bigrams → stopwords → unique set."""
    tokens = _tokenize(text)
    tokens = _apply_thesaurus(tokens)
    tokens = _handle_bigrams(tokens)
    tokens = _remove_stopwords(tokens)
    return set(tokens)


# ── Co-occurrence logic ──────────────────────────────────────────────────────

def build_cooccurrence_matrix(
    df: pd.DataFrame,
    target_terms: list[str],
) -> pd.DataFrame:
    """Return a symmetric len(target_terms) x len(target_terms) co-occurrence
    DataFrame (diagonal = 0, binary counting per document)."""
    n = len(target_terms)
    term_idx = {t: i for i, t in enumerate(target_terms)}
    matrix = np.zeros((n, n), dtype=int)

    for _, row in df.iterrows():
        text = _combine_text(row)
        doc_terms = extract_terms(text)
        # Keep only terms in the target set
        present = sorted(doc_terms & set(target_terms))
        for a, b in combinations(present, 2):
            i, j = term_idx[a], term_idx[b]
            matrix[i, j] += 1
            matrix[j, i] += 1

    return pd.DataFrame(matrix, index=target_terms, columns=target_terms)


# ── Per-term metrics ─────────────────────────────────────────────────────────

def compute_term_metrics(cooc: pd.DataFrame) -> pd.DataFrame:
    """Compute links (non-zero neighbours) and TLS (row sum) per term."""
    links = (cooc > 0).sum(axis=1)
    tls = cooc.sum(axis=1)
    return pd.DataFrame({"links_python": links, "tls_python": tls})


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    setup_matplotlib()

    # Load data
    print("Loading WoS records …")
    df_wos = load_savedrecs()
    print(f"  {len(df_wos)} records loaded.")

    print("Loading VOSViewer keyword map …")
    df_vos = load_vosviewer_map()
    target_terms = sorted(df_vos["label"].str.lower().tolist())
    print(f"  {len(target_terms)} target terms: {target_terms[:5]} … {target_terms[-3:]}")

    # --- 1. Count per-term occurrences (binary) for correlation later --------
    print("\nCounting per-term occurrences (binary) …")
    occ_counts: dict[str, int] = {t: 0 for t in target_terms}
    for _, row in df_wos.iterrows():
        text = _combine_text(row)
        doc_terms = extract_terms(text)
        for t in doc_terms & set(target_terms):
            occ_counts[t] += 1

    # --- 2. Build co-occurrence matrix ---------------------------------------
    print("Building 28×28 co-occurrence matrix …")
    cooc = build_cooccurrence_matrix(df_wos, target_terms)

    # --- 3. Save matrix to CSV -----------------------------------------------
    csv_path = MEDIA_DIR / "cooccurrence_matrix.csv"
    cooc.to_csv(csv_path)
    print(f"\nCo-occurrence matrix saved → {csv_path}")

    # --- 4. Per-term metrics -------------------------------------------------
    metrics = compute_term_metrics(cooc)
    metrics["occurrences_python"] = [occ_counts[t] for t in target_terms]

    # Merge with VOSViewer values
    vos_lookup = df_vos.set_index(df_vos["label"].str.lower())
    metrics["links_vos"] = [int(vos_lookup.loc[t, "links"]) for t in target_terms]
    metrics["tls_vos"] = [int(vos_lookup.loc[t, "tls"]) for t in target_terms]
    metrics["occurrences_vos"] = [int(vos_lookup.loc[t, "occurrences"]) for t in target_terms]
    metrics.index = target_terms
    metrics.index.name = "term"

    # --- 5. Print comparison table -------------------------------------------
    print("\n" + "=" * 90)
    print(f"{'term':<20s} {'links_py':>8s} {'links_vos':>9s}   "
          f"{'tls_py':>8s} {'tls_vos':>9s}   "
          f"{'occ_py':>8s} {'occ_vos':>9s}")
    print("-" * 90)
    for t in target_terms:
        r = metrics.loc[t]
        print(f"{t:<20s} {r['links_python']:8d} {r['links_vos']:9d}   "
              f"{r['tls_python']:8d} {r['tls_vos']:9d}   "
              f"{r['occurrences_python']:8d} {r['occurrences_vos']:9d}")
    print("=" * 90)

    # --- 6. Correlations -----------------------------------------------------
    r_tls, p_tls = pearsonr(metrics["tls_python"], metrics["tls_vos"])
    r_occ, p_occ = pearsonr(metrics["occurrences_python"], metrics["occurrences_vos"])

    print(f"\nPearson r  (TLS Python vs VOSViewer):         {r_tls:.4f}  (p = {p_tls:.2e})")
    print(f"Pearson r  (Occurrences Python vs VOSViewer):  {r_occ:.4f}  (p = {p_occ:.2e})")


if __name__ == "__main__":
    main()
