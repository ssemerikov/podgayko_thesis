"""
Verify all bibliography entries against Crossref.

For each @entry with a DOI:
  1. Query https://api.crossref.org/works/{doi}
  2. Compare: title (fuzzy), first-author surname, year
  3. Report mismatches.

For each @entry WITHOUT a DOI:
  1. Search Crossref by title (top 3 results)
  2. Suggest a candidate DOI if title+author match.

Outputs:
  - data/bib_verification_report.csv  — machine-readable findings
  - prints summary to stdout

Usage: python3 scripts/verify_bib_crossref.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

import bibtexparser

ROOT = Path(__file__).resolve().parent.parent
BIB_FILES = [ROOT / "capstone.bib", ROOT / "scopus.bib"]
OUT_CSV = ROOT / "data" / "bib_verification_report.csv"
USER_AGENT = "PodgayikoBachelorThesis/1.0 (mailto:serhi.pidhaykoy@gmail.com)"
REQUEST_DELAY = 0.4  # politeness, ~2.5 req/sec


LATEX_ACCENT_MAP = {
    r"\\'a": "á", r"\\'e": "é", r"\\'i": "í", r"\\'o": "ó", r"\\'u": "ú",
    r'\\"a': "ä", r'\\"o': "ö", r'\\"u': "ü", r'\\"e': "ë",
    r"\\^a": "â", r"\\^e": "ê", r"\\^i": "î", r"\\^o": "ô",
    r"\\`a": "à", r"\\`e": "è", r"\\`o": "ò",
    r"\\~n": "ñ", r"\\~a": "ã", r"\\~o": "õ",
    r"\\v\{c\}": "č", r"\\v\{s\}": "š", r"\\v\{z\}": "ž",
    r"\\c\{c\}": "ç", r"\\c\{s\}": "ş",
    r"\\AA": "Å", r"\\aa": "å", r"\\O": "Ø", r"\\o": "ø",
}


def latex_to_unicode(s: str) -> str:
    """Convert LaTeX accents like \\'a, \\"o to Unicode á, ö."""
    for tex, uni in LATEX_ACCENT_MAP.items():
        s = re.sub(tex, uni, s)
    return s


def normalize(s: str) -> str:
    s = latex_to_unicode(s)
    s = re.sub(r"[{}\\]", "", s).lower()
    s = re.sub(r"[^a-zа-яёіїєґáéíóúäöüâêîôàèòñãõčšžçşåø0-9 ]+", " ", s, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", s).strip()


def strip_diacritics(s: str) -> str:
    """Strip diacritics for diacritic-insensitive author matching."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def _has_cyrillic(s: str) -> bool:
    return bool(re.search(r"[а-яёіїєґА-ЯЁІЇЄҐ]", s))


def crossref_get(doi: str) -> dict | None:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8")).get("message")
    except Exception as e:
        return {"_error": str(e)}


def crossref_search(title: str, author_surname: str = "", rows: int = 3) -> list[dict]:
    qtitle = urllib.parse.quote(title[:100])
    url = f"https://api.crossref.org/works?query.title={qtitle}&rows={rows}"
    if author_surname:
        url += f"&query.author={urllib.parse.quote(author_surname)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))["message"]["items"]
    except Exception:
        return []


def first_author_surname(entry: dict) -> str:
    a = entry.get("author", "")
    if not a:
        return ""
    first = a.split(" and ")[0]
    if "," in first:
        return first.split(",")[0].strip()
    parts = first.strip().split()
    return parts[-1] if parts else ""


def crossref_first_author_surname(msg: dict) -> tuple[str, bool]:
    """Return (surname, is_institutional). Institutional authors have only
    'name' field, no 'family/given'. Many Ukrainian/Indian journal deposits
    register the parent institution as author."""
    if not msg.get("author"):
        return "", False
    a = msg["author"][0]
    if "family" in a:
        return a["family"], False
    if "name" in a:
        return a["name"], True
    return "", False


def crossref_year(msg: dict) -> str:
    """Return print year if available (canonical citation year),
    else online year, else issued, else created (Crossref deposit date)."""
    for f in ("published-print", "published", "published-online", "issued", "created"):
        d = msg.get(f, {}).get("date-parts", [[]])
        if d and d[0] and d[0][0] is not None:
            return str(d[0][0])
    return ""


def main() -> int:
    OUT_CSV.parent.mkdir(exist_ok=True)
    rows: list[dict] = []
    n_total = 0
    n_with_doi = 0
    n_doi_ok = 0
    n_doi_404 = 0
    n_title_mismatch = 0
    n_author_mismatch = 0
    n_year_mismatch = 0
    n_no_doi = 0

    for bib_file in BIB_FILES:
        with bib_file.open(encoding="utf-8") as fh:
            db = bibtexparser.load(fh)
        for e in db.entries:
            n_total += 1
            key = e["ID"]
            etype = e["ENTRYTYPE"]
            doi = (e.get("doi") or "").strip()
            title = (e.get("title") or "").strip()
            year = (e.get("year") or "").strip()
            surname = first_author_surname(e)

            row: dict = {
                "key": key, "type": etype, "doi": doi,
                "title_local": title[:80], "year_local": year, "first_author": surname,
                "status": "", "title_sim": "", "year_remote": "",
                "author_remote": "", "issue": "", "suggestion": "",
            }

            if not doi:
                n_no_doi += 1
                # Skip search for non-research types
                if etype in ("misc", "techreport", "book") and not title:
                    row["status"] = "no_doi_skipped"
                else:
                    row["status"] = "no_doi"
                    candidates = crossref_search(title, surname)
                    if candidates:
                        c = candidates[0]
                        c_title = c.get("title", [""])[0]
                        sim = title_similarity(title, c_title)
                        if sim >= 0.85:
                            row["suggestion"] = f"DOI {c.get('DOI')} sim={sim:.2f}"
                            row["issue"] = "no_doi_but_found"
                        else:
                            row["suggestion"] = f"top result: {c.get('DOI')} sim={sim:.2f}"
                    time.sleep(REQUEST_DELAY)
                rows.append(row)
                continue

            n_with_doi += 1
            msg = crossref_get(doi)
            time.sleep(REQUEST_DELAY)
            if not msg:
                n_doi_404 += 1
                row["status"] = "doi_404"
                row["issue"] = "DOI not resolved"
                rows.append(row)
                continue
            if "_error" in msg:
                err = msg["_error"]
                if "404" in err:
                    n_doi_404 += 1
                    row["status"] = "doi_404"
                    row["issue"] = "DOI 404"
                else:
                    row["status"] = "doi_error"
                    row["issue"] = err[:80]
                rows.append(row)
                continue

            # Validate title, year, author
            r_title = (msg.get("title") or [""])[0]
            r_subtitle = (msg.get("subtitle") or [""])
            if r_subtitle and r_subtitle[0]:
                r_title_full = f"{r_title}: {r_subtitle[0]}"
            else:
                r_title_full = r_title
            r_year = crossref_year(msg)
            r_author, r_is_inst = crossref_first_author_surname(msg)

            sim = max(title_similarity(title, r_title), title_similarity(title, r_title_full))
            row["title_sim"] = f"{sim:.2f}"
            row["year_remote"] = r_year
            row["author_remote"] = r_author + (" [INST]" if r_is_inst else "")

            issues = []
            if sim < 0.7 and not _has_cyrillic(r_title) and not _has_cyrillic(title):
                issues.append("title_low_sim")
                n_title_mismatch += 1
            if year and r_year and year != r_year:
                issues.append(f"year_diff({year}≠{r_year})")
                n_year_mismatch += 1
            if surname and r_author and not r_is_inst:
                ns = normalize(surname)
                nr = normalize(r_author)
                # diacritic-insensitive comparison (Rajamäki ≈ Rajamaki)
                ns_d = strip_diacritics(ns)
                nr_d = strip_diacritics(nr)
                # allow Cyrillic-Latin transliteration matches (skip when one is Cyrillic)
                cyrillic_mismatch = _has_cyrillic(ns) != _has_cyrillic(nr)
                same_or_substring = (
                    ns == nr or ns_d == nr_d
                    or nr_d in ns_d or ns_d in nr_d
                )
                if not (same_or_substring or cyrillic_mismatch):
                    issues.append(f"author_diff({surname}≠{r_author})")
                    n_author_mismatch += 1

            if issues:
                row["status"] = "doi_resolved_with_issues"
                row["issue"] = ", ".join(issues)
            else:
                n_doi_ok += 1
                row["status"] = "doi_ok"

            rows.append(row)

            print(f"  [{n_total:3d}] {key:40s} {row['status']:30s} {row.get('issue', ''):40s}")

    # Write CSV
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n" + "=" * 60)
    print(f"Total entries:                 {n_total}")
    print(f"  With DOI:                    {n_with_doi}")
    print(f"    DOI ok (full match):       {n_doi_ok}")
    print(f"    DOI 404 / unresolved:      {n_doi_404}")
    print(f"    Title low similarity:      {n_title_mismatch}")
    print(f"    Year mismatch:             {n_year_mismatch}")
    print(f"    Author mismatch:           {n_author_mismatch}")
    print(f"  Without DOI:                 {n_no_doi}")
    print(f"\nReport written to: {OUT_CSV.relative_to(ROOT)}")
    return 0 if (n_doi_404 == 0 and n_title_mismatch == 0 and n_year_mismatch == 0
                  and n_author_mismatch == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
