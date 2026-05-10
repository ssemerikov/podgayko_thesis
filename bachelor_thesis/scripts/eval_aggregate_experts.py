"""
Агрегація CSV-відповідей експертного оцінювання прототипу.

Зчитує усі `raw_responses_EXP-*.csv` з каталогу `expert_eval/`, валідує схему,
обчислює описові SUS-метрики (нормалізація 0--100), доменні B-блок-метрики,
TRL-розподіл, і експортує:

  - `expert_eval/responses_anonymized.csv`  — зведений CSV
  - `expert_eval/results_table.tex`         — LaTeX-таблиця для \input{...}
  - `expert_eval/summary_stats.json`        — машино-читаний звіт

Якісне тематичне кодування C-блоку та B-коментарів виконується вручну
(автор + керівник) і фіксується у `expert_eval/summary.md`.

Уважно з $n{<}12$: середні та SD мають широкий 95%-CI ($\pm 25$ балів для SUS).
Скрипт виводить попередження для $n{<}12$ і **не** обчислює інференційні
тести (Cronbach $\alpha$ для $n=3$ не має змістовного значення).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import mean, stdev

import pandas as pd

EVAL_DIR = Path(__file__).resolve().parent.parent / "expert_eval"

SUS_COLS = [f"sus_a{i}" for i in range(1, 11)]
B_SCORE_COLS = [f"b{i}_score" for i in range(1, 9)]
B_COMMENT_COLS = [f"b{i}_comment" for i in range(1, 9)]
B_LABELS = {
    "b1_score": "B.1 Specifikatsiya v2.0 form alignment",
    "b2_score": "B.2 Cross-form warnings clarity",
    "b3_score": "B.3 Roles & territorial binding",
    "b4_score": "B.4 Suitability for management decisions",
    "b5_score": "B.5 Displaced institutions accommodation",
    "b6_score": "B.6 IDP/veterans accommodation",
    "b7_score": "B.7 Audit trail reliability",
    "b8_score": "B.8 Implementation likelihood",
}
B_LABELS_UK = {
    "b1_score": "B.1 Відповідність полів Specifikatsiya v2.0",
    "b2_score": "B.2 Зрозумілість крос-формових попереджень",
    "b3_score": "B.3 Адекватність ролей та територіальної прив'язки",
    "b4_score": "B.4 Придатність для управлінських рішень",
    "b5_score": "B.5 Готовність обліковувати переміщені заклади",
    "b6_score": "B.6 Готовність обліковувати ВПО та ветеранів",
    "b7_score": "B.7 Очікувана надійність аудит-trail",
    "b8_score": "B.8 Імовірність впровадження",
}


def normalize_sus(row: pd.Series) -> float:
    """Standard SUS normalization to 0–100. Odd items: score-1; even: 5-score."""
    raw = []
    for i, col in enumerate(SUS_COLS):
        v = row[col]
        if pd.isna(v):
            return float("nan")
        v = int(v)
        if i % 2 == 0:  # A.1, A.3, A.5, A.7, A.9 (odd in 1-indexed)
            raw.append(v - 1)
        else:           # A.2, A.4, A.6, A.8, A.10 (even in 1-indexed)
            raw.append(5 - v)
    return sum(raw) * 2.5  # multiply by 2.5 → 0..100 scale


def descriptive(values: list[float]) -> dict[str, float]:
    """Robust descriptive stats. Returns NaN for n < 1."""
    clean = [v for v in values if not pd.isna(v)]
    n = len(clean)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "sd": float("nan"),
                "min": float("nan"), "max": float("nan")}
    return {
        "n": n,
        "mean": round(mean(clean), 2),
        "sd": round(stdev(clean), 2) if n >= 2 else float("nan"),
        "min": min(clean),
        "max": max(clean),
    }


def fmt(v: float | int) -> str:
    """Format for LaTeX table cells. NaN → em-dash."""
    if isinstance(v, float) and math.isnan(v):
        return "---"
    if isinstance(v, float):
        return f"{v:.2f}".replace(".", "{,}")
    return str(v)


def load_responses(csv_paths: list[Path]) -> pd.DataFrame:
    frames = []
    for p in csv_paths:
        try:
            df = pd.read_csv(p, encoding="utf-8")
        except Exception as e:
            print(f"  WARN: cannot read {p.name}: {e}", file=sys.stderr)
            continue
        if "respondent_code" not in df.columns:
            df["respondent_code"] = p.stem.replace("raw_responses_", "")
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def export_results_table(stats: dict, out_path: Path) -> None:
    n = stats.get("n_total", 0)
    n_str = str(n) if n else "TBD"

    sus_mean = fmt(stats["sus"]["mean"])
    sus_sd = fmt(stats["sus"]["sd"])

    rows: list[str] = []
    rows.append(
        f"\\textbf{{A. SUS, нормалізований 0--100}} & {n} & {sus_mean} & {sus_sd} & {stats['sus_interpretation']} \\\\"
    )
    rows.append("\\hline")

    for col in B_SCORE_COLS:
        d = stats["b"][col]
        rows.append(
            f"{B_LABELS_UK[col]} & {d['n']} & {fmt(d['mean'])} & {fmt(d['sd'])} & --- \\\\"
        )
        rows.append("\\hline")

    b_avg = stats["b_avg"]
    rows.append(
        f"\\textbf{{B. Усереднена доменна оцінка (1--5)}} & {b_avg['n']} & {fmt(b_avg['mean'])} & {fmt(b_avg['sd'])} & --- \\\\"
    )
    rows.append("\\hline")

    trl = stats["trl"]
    rows.append(
        f"\\textbf{{C.4 Self-assessed TRL (1--9)}} & {trl['n']} & {fmt(trl['mean'])} & {fmt(trl['sd'])} & --- \\\\"
    )
    rows.append("\\hline")

    table_body = "\n".join(rows)

    text = f"""% Auto-generated by scripts/eval_aggregate_experts.py
% Do NOT edit by hand. Re-run aggregation script after new responses arrive.

\\begin{{table}}[htbp]
\\centering
\\caption{{Зведені описові метрики експертного оцінювання прототипу системи моніторингу П(ПТ)О ($n${"="}{n_str}).}}
\\label{{tab:expert_eval_results}}
\\small
\\setlength\\tabcolsep{{4pt}}
\\renewcommand{{\\arraystretch}}{{1.1}}
\\begin{{tabular}}{{|p{{0.42\\linewidth}}|c|c|c|p{{0.20\\linewidth}}|}}
\\hline
\\textbf{{Метрика}} & $n$ & \\textbf{{M}} & \\textbf{{SD}} & \\textbf{{Інтерпретація}} \\\\
\\hline
{table_body}
\\end{{tabular}}

\\medskip

\\footnotesize
\\textit{{Примітка}}: при $n{{<}}12$ числові середні та стандартні відхилення служать описовим пріором, не дозволяють інференційних висновків (Sauro \\& Lewis, 2016). Основа аналізу~--- якісне тематичне кодування блоку~C та~B-коментарів разом з~think-aloud нотатками half-day сесій (підрозділ~\\ref{{sec:p2-eval-expert}}).

\\normalsize
\\end{{table}}
"""
    out_path.write_text(text, encoding="utf-8")
    print(f"  wrote {out_path.relative_to(out_path.parent.parent)}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-glob", default="raw_responses_EXP-*.csv",
                   help="Glob pattern relative to expert_eval/")
    p.add_argument("--output-csv", default="responses_anonymized.csv")
    p.add_argument("--output-tex", default="results_table.tex")
    p.add_argument("--output-json", default="summary_stats.json")
    args = p.parse_args(argv)

    csv_paths = sorted(EVAL_DIR.glob(args.input_glob))
    print(f"Scanning {EVAL_DIR.relative_to(EVAL_DIR.parent.parent)} for {args.input_glob}")
    print(f"Found {len(csv_paths)} response file(s).")

    if not csv_paths:
        print("\nNo responses yet — generating placeholder results_table.tex with TBD.")
        empty_stats = {
            "n_total": 0,
            "sus": {"n": 0, "mean": float("nan"), "sd": float("nan"),
                     "min": float("nan"), "max": float("nan")},
            "sus_interpretation": "TBD",
            "b": {col: descriptive([]) for col in B_SCORE_COLS},
            "b_avg": descriptive([]),
            "trl": descriptive([]),
        }
        export_results_table(empty_stats, EVAL_DIR / args.output_tex)
        (EVAL_DIR / args.output_json).write_text(json.dumps(empty_stats, indent=2), encoding="utf-8")
        return 0

    df = load_responses(csv_paths)
    print(f"Loaded {len(df)} response row(s).")

    # SUS normalization per respondent
    df["sus_normalized"] = df.apply(normalize_sus, axis=1)
    sus_stats = descriptive(df["sus_normalized"].tolist())

    # B-block per item
    b_stats = {col: descriptive(df[col].dropna().astype(float).tolist())
               for col in B_SCORE_COLS}

    # B-block average per respondent (mean of 8 items)
    df["b_avg"] = df[B_SCORE_COLS].astype(float).mean(axis=1)
    b_avg_stats = descriptive(df["b_avg"].dropna().tolist())

    # TRL (column c4_trl)
    if "c4_trl" in df.columns:
        trl_stats = descriptive(df["c4_trl"].dropna().astype(float).tolist())
    else:
        trl_stats = descriptive([])

    # SUS interpretation guidance (per Bangor et al. 2009 adjective scale; n>12 only)
    if sus_stats["n"] >= 12:
        m = sus_stats["mean"]
        if m >= 80.3:
            interp = "Excellent (Bangor)"
        elif m >= 68:
            interp = "Above average"
        elif m >= 50.9:
            interp = "Average"
        else:
            interp = "Below average"
    else:
        interp = f"описовий пріор ($n{{=}}{sus_stats['n']}{{<}}12$)"

    stats = {
        "n_total": sus_stats["n"],
        "sus": sus_stats,
        "sus_interpretation": interp,
        "b": b_stats,
        "b_avg": b_avg_stats,
        "trl": trl_stats,
        "warning": "n < 12 — SUS-середнє має 95%-CI приблизно ±25 балів; не інтерпретувати як абсолютне значення."
                  if sus_stats["n"] < 12 else None,
    }

    print(f"\nSUS (нормалізований 0–100):")
    print(f"  n={sus_stats['n']}, M={fmt(sus_stats['mean'])}, SD={fmt(sus_stats['sd'])}")
    if sus_stats["n"] < 12:
        print(f"  WARN: n<12 — описовий пріор; не інференційне.")

    print(f"\nB-блок (1–5):")
    for col, label in B_LABELS_UK.items():
        d = b_stats[col]
        print(f"  {label}: n={d['n']}, M={fmt(d['mean'])}, SD={fmt(d['sd'])}")

    print(f"\nTRL self-assessment (1–9): n={trl_stats['n']}, M={fmt(trl_stats['mean'])}")

    # Anonymize and export
    anon_cols = [c for c in df.columns if c not in ("respondent_email", "respondent_name")]
    anon_df = df[anon_cols].copy()
    anon_df.to_csv(EVAL_DIR / args.output_csv, index=False, encoding="utf-8")
    print(f"\nWrote {args.output_csv}")

    export_results_table(stats, EVAL_DIR / args.output_tex)
    (EVAL_DIR / args.output_json).write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.output_json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
