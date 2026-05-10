"""
Fallback-парсер заповнюваного PDF з рубрикою експертного оцінювання у CSV.

Використовується, коли експерт надав перевагу offline-формату (PDF замість
Google Form). Зчитує форм-поля з PDF (radio-groups SUS A.1–A.10, шкали
B.1–B.8, текстові поля C.1–C.4, метадані D.1–D.6) і експортує
`raw_responses_EXP-<n>.csv` у тій самій схемі, що й Google Form
(див. `expert_eval/08_form_schema.md`).

Залежності: pypdf >=4.0 (PDF AcroForm parser).

Використання:
  python eval_pdf_to_csv.py path/to/06_rubric_fillable_filled.pdf EXP-<n>
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf>=4.0", file=sys.stderr)
    sys.exit(1)

EVAL_DIR = Path(__file__).resolve().parent.parent / "expert_eval"

# Поля у заповнюваному PDF, у тому самому порядку, що й CSV header.
EXPECTED_FIELDS = [
    *[f"sus_a{i}" for i in range(1, 11)],
    "b1_score", "b1_comment",
    "b2_score", "b2_comment",
    "b3_score", "b3_comment",
    "b4_score", "b4_comment",
    "b5_score", "b5_comment",
    "b6_score", "b6_comment",
    "b7_score", "b7_comment",
    "b8_score", "b8_comment",
    "c1_text", "c2_text", "c3_text",
    "c4_trl", "c4_justification",
    "d1_role", "d1_other", "d2_region", "d2_other",
    "d3_experience", "d4_displaced", "d5_tech_level", "d6_halfday",
    "duration_min", "tech_issues", "tech_issues_text",
]

CSV_HEADER = ["respondent_code", "timestamp"] + EXPECTED_FIELDS


def extract_form_fields(pdf_path: Path) -> dict[str, Any]:
    """Read filled form fields from PDF AcroForm."""
    reader = PdfReader(pdf_path)
    fields = reader.get_form_text_fields() or {}
    # AcroForm radio groups appear as text values too in pypdf; merge w/ checkboxes.
    fields_extra = reader.get_fields() or {}
    out: dict[str, Any] = {}
    for name, raw in fields_extra.items():
        # Spec: each Field is a dict-like; "/V" is the value.
        v = raw.get("/V") if hasattr(raw, "get") else None
        if v is None:
            v = fields.get(name)
        if v is not None:
            # PDF stores booleans as /Yes etc.; flatten to plain str.
            out[name] = str(v).strip("/").strip()
    return out


def normalize_field_value(field: str, value: Any) -> str:
    """Coerce PDF-form values into CSV-clean strings."""
    if value is None:
        return ""
    s = str(value).strip()
    # SUS/B numeric scales: keep digit only.
    if field.startswith("sus_") or field.endswith("_score") or field == "c4_trl":
        for ch in s:
            if ch.isdigit():
                return ch
        return ""
    # D.* mostly enum: use as-is.
    return s


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path, help="Path to filled `06_rubric_fillable_filled.pdf`")
    p.add_argument("expert_code", help="Expert code, e.g. EXP-1")
    p.add_argument("--output-dir", type=Path, default=EVAL_DIR,
                   help="Directory to write `raw_responses_<code>.csv`")
    args = p.parse_args(argv)

    if not args.pdf.exists():
        print(f"ERROR: file not found: {args.pdf}", file=sys.stderr)
        return 1

    print(f"Reading {args.pdf}...")
    fields = extract_form_fields(args.pdf)
    print(f"Found {len(fields)} form fields.")

    missing = [f for f in EXPECTED_FIELDS if f not in fields]
    if missing:
        print(f"WARN: missing {len(missing)} expected fields:")
        for f in missing[:10]:
            print(f"  - {f}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    row = {f: normalize_field_value(f, fields.get(f, "")) for f in EXPECTED_FIELDS}
    row["respondent_code"] = args.expert_code
    row["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    out_csv = args.output_dir / f"raw_responses_{args.expert_code}.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_HEADER)
        w.writeheader()
        w.writerow(row)

    print(f"\nWrote {out_csv}")
    print(f"Rows: 1 (expert code = {args.expert_code})")
    print(f"\nNext step: run `python eval_aggregate_experts.py` to update results_table.tex.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
