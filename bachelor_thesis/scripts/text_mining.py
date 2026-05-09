"""
Text mining from WoS titles and abstracts — replicates VOSViewer's methodology.

Steps:
1. Combine TI + AB per record, lowercase
2. Tokenize words (length >= 2)
3. Binary counting (each word max once per document)
4. Apply thesaurus (VET variants → "vet", student variants → "student")
5. Remove stopwords + domain excludes
6. Filter to occurrences >= 100
7. Compare with VOSViewer's 28 keywords
8. Save term_frequencies.csv
"""

import re
import sys
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# Import from shared parser in the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wos_parser import load_savedrecs, load_vosviewer_map, MEDIA_DIR, setup_matplotlib


# ── Thesaurus ────────────────────────────────────────────────────────────────
# VOSViewer merged VET-related and student-related variants.
THESAURUS = {
    # VET variants
    "vocational": "vet",
    "tvet": "vet",
    "apprenticeship": "vet",
    "apprenticeships": "vet",
    "vocation": "vet",
    "vocations": "vet",
    # Student variants
    "students": "student",
    "learners": "student",
    "learner": "student",
    "trainees": "student",
    "trainee": "student",
    "pupils": "student",
    "pupil": "student",
    "apprentice": "student",
    "apprentices": "student",
    # Morphological variants for the 28 VOSViewer keywords
    "skills": "skill",
    "skilled": "skill",
    "teachers": "teacher",
    "teaching": "teacher",
    "studies": "study",
    "studying": "study",
    "studied": "study",
    "schools": "school",
    "schooling": "school",
    "assessments": "assessment",
    "assessed": "assessment",
    "assessing": "assessment",
    "models": "model",
    "modelling": "model",
    "modeling": "model",
    "modeled": "model",
    "modelled": "model",
    "performances": "performance",
    "performed": "performance",
    "performing": "performance",
    "effects": "effect",
    "effective": "effect",
    "effectively": "effect",
    "effectiveness": "effect",
    "developments": "development",
    "developing": "development",
    "developed": "development",
    "differences": "difference",
    "different": "difference",
    "differently": "difference",
    "groups": "group",
    "grouped": "group",
    "grouping": "group",
    "practices": "practice",
    "practiced": "practice",
    "practicing": "practice",
    "practical": "practice",
    "competences": "competence",
    "competencies": "competence",
    "competency": "competence",
    "competent": "competence",
    "problems": "problem",
    "problematic": "problem",
    "contexts": "context",
    "contextual": "context",
    "countries": "country",
    "fields": "field",
    "papers": "paper",
    "orders": "order",
    "ordered": "order",
    "ordering": "order",
    "companies": "company",
    "works": "work",
    "worked": "work",
    "working": "work",
    "workers": "work",
    "worker": "work",
    "workplace": "work",
    "workplaces": "work",
    "learned": "learning",
    "learns": "learning",
}

# ── Domain excludes ──────────────────────────────────────────────────────────
DOMAIN_EXCLUDES = {"article", "patient", "year"}

# ── English stopwords (~174 common words) ────────────────────────────────────
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "also", "am",
    "an", "and", "any", "are", "aren", "arent", "as", "at", "be", "because",
    "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "cannot", "could", "couldn", "couldnt", "did", "didn", "didnt", "do",
    "does", "doesn", "doesnt", "doing", "don", "dont", "down", "during",
    "each", "few", "for", "from", "further", "get", "got", "had", "hadn",
    "hadnt", "has", "hasn", "hasnt", "have", "haven", "havent", "having",
    "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "however", "if", "in", "into", "is", "isn", "isnt", "it", "its", "itself",
    "just", "ll", "may", "me", "might", "more", "most", "must", "mustn",
    "mustnt", "my", "myself", "need", "needn", "no", "nor", "not", "now",
    "of", "off", "on", "once", "only", "or", "other", "our", "ours",
    "ourselves", "out", "over", "own", "re", "same", "shall", "shan", "shant",
    "she", "should", "shouldn", "shouldnt", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under",
    "until", "up", "ve", "very", "was", "wasn", "wasnt", "we", "were",
    "weren", "werent", "what", "when", "where", "which", "while", "who",
    "whom", "why", "will", "with", "won", "wont", "would", "wouldn",
    "wouldnt", "you", "your", "yours", "yourself", "yourselves",
}

# ── Known multi-word VOSViewer terms ─────────────────────────────────────────
# Only "higher education" among the 28 keywords is multi-word.
MULTIWORD_TERMS = {
    ("higher", "education"): "higher education",
}


def tokenize_document(text: str) -> set[str]:
    """Tokenize text into a set of unique lowercase words (length >= 2).

    Also detects known multi-word terms (bigrams) and removes component words
    that were consumed by a multi-word term to avoid double counting.
    """
    words = re.findall(r"\b[a-z]{2,}\b", text.lower())
    word_set = set(words)

    # Check for multi-word terms
    consumed = set()
    multiword_found = set()
    for (w1, w2), term in MULTIWORD_TERMS.items():
        if w1 in word_set and w2 in word_set:
            multiword_found.add(term)
            # Remove the first component to avoid double counting
            # (keep "education" since it's not a separate VOSViewer keyword)
            consumed.add(w1)

    # Apply thesaurus BEFORE building the final set
    final = set()
    for w in word_set:
        if w in consumed:
            continue
        mapped = THESAURUS.get(w, w)
        final.add(mapped)

    # Add multi-word terms
    final |= multiword_found

    return final


def build_frequency_table(df: pd.DataFrame) -> pd.Series:
    """Build binary occurrence counts across all documents.

    For each document, TI + AB are combined, tokenized, thesaurus-mapped,
    and deduplicated. Then we count how many documents each term appears in.
    """
    counter: Counter = Counter()

    for _, row in df.iterrows():
        title = str(row.get("TI", "")) if pd.notna(row.get("TI")) else ""
        abstract = str(row.get("AB", "")) if pd.notna(row.get("AB")) else ""
        combined = title + " " + abstract

        terms = tokenize_document(combined)

        # Remove stopwords and domain excludes
        terms -= STOPWORDS
        terms -= DOMAIN_EXCLUDES

        counter.update(terms)

    freq = pd.Series(counter, dtype=int).sort_values(ascending=False)
    return freq


def main():
    setup_matplotlib()

    # ── 1. Load data ─────────────────────────────────────────────────────────
    print("Loading WoS records...")
    df_wos = load_savedrecs()
    print(f"  {len(df_wos)} records loaded")
    print(f"  Columns: {list(df_wos.columns[:10])}...")

    print("\nLoading VOSViewer keyword map...")
    df_vos = load_vosviewer_map()
    print(f"  {len(df_vos)} keywords")

    # ── 2. Build frequency table ─────────────────────────────────────────────
    print("\nBuilding term frequency table (binary counting)...")
    freq = build_frequency_table(df_wos)
    print(f"  Total unique terms: {len(freq)}")

    # ── 3. Filter to occurrences >= 100 ──────────────────────────────────────
    freq_100 = freq[freq >= 100]
    print(f"  Terms with occurrences >= 100: {len(freq_100)}")

    print("\n" + "=" * 60)
    print("FULL FREQUENCY TABLE (occurrences >= 100)")
    print("=" * 60)
    for term, count in freq_100.items():
        print(f"  {term:<25s} {count:>5d}")

    # ── 4. Compare with VOSViewer's 28 keywords ─────────────────────────────
    vos_keywords = dict(zip(df_vos["label"].str.lower(), df_vos["occurrences"]))

    print("\n" + "=" * 60)
    print("COMPARISON: Python vs VOSViewer (28 keywords)")
    print("=" * 60)
    print(f"  {'Keyword':<25s} {'Python':>8s} {'VOSViewer':>10s} {'Diff':>8s}")
    print("  " + "-" * 55)

    comparison_rows = []
    matched_python = []
    matched_vos = []

    for kw in sorted(vos_keywords.keys()):
        vos_count = vos_keywords[kw]
        py_count = freq.get(kw, 0)
        diff = py_count - vos_count
        sign = "+" if diff > 0 else ""
        print(f"  {kw:<25s} {py_count:>8d} {vos_count:>10d} {sign}{diff:>7d}")

        comparison_rows.append({
            "term": kw,
            "occurrences_python": py_count,
            "occurrences_vos": vos_count,
        })
        matched_python.append(py_count)
        matched_vos.append(vos_count)

    # ── 5. Pearson correlation ───────────────────────────────────────────────
    r, p = pearsonr(matched_python, matched_vos)
    print(f"\n  Pearson correlation (n={len(matched_python)}): r = {r:.4f}, p = {p:.2e}")

    # ── 6. Build output CSV ──────────────────────────────────────────────────
    # All terms with occurrences >= 100, with VOSViewer count where available
    output_rows = []
    for term, count in freq_100.items():
        output_rows.append({
            "term": term,
            "occurrences_python": count,
            "occurrences_vos": vos_keywords.get(term, np.nan),
        })

    # Also add any VOSViewer keywords that fell below threshold in Python
    python_terms_100 = set(freq_100.index)
    for kw, vos_count in vos_keywords.items():
        if kw not in python_terms_100:
            output_rows.append({
                "term": kw,
                "occurrences_python": int(freq.get(kw, 0)),
                "occurrences_vos": vos_count,
            })

    df_out = pd.DataFrame(output_rows)
    df_out = df_out.sort_values("occurrences_python", ascending=False).reset_index(drop=True)

    csv_path = MEDIA_DIR / "term_frequencies.csv"
    df_out.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")
    print(f"  {len(df_out)} rows ({len(freq_100)} terms >= 100 + "
          f"{len(df_out) - len(freq_100)} VOSViewer-only terms below threshold)")


if __name__ == "__main__":
    main()
