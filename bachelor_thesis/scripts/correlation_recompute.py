"""
Recompute Pearson and Spearman correlations between the Python-replicated
metrics and the original VOSViewer metrics, with Fisher-z 95% confidence
intervals and Bonferroni adjustment for the 7 simultaneous tests.

Addresses Reviewer #1's concern (R1-#5) that the original report quoted
Pearson r without CI, without Spearman alternative, and without
multiple-comparisons correction.

Reads `media/table_comparison.csv` produced by `comparison.py`.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from wos_parser import ROOT_DIR

INPUT_CSV = ROOT_DIR / "media" / "table_comparison.csv"
OUTPUT_CSV = ROOT_DIR / "data" / "correlation_recompute.csv"


def fisher_z_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Two-sided 100·(1-alpha)% Fisher-z confidence interval for Pearson r."""
    if not (-1 < r < 1) or n < 4:
        return (float("nan"), float("nan"))
    z = math.atanh(r)
    se = 1 / math.sqrt(n - 3)
    z_crit = 1.959963984540054  # qnorm(0.975), close enough for 95%
    if alpha != 0.05:
        from scipy.stats import norm
        z_crit = float(norm.ppf(1 - alpha / 2))
    lo, hi = z - z_crit * se, z + z_crit * se
    return (math.tanh(lo), math.tanh(hi))


def safe_pair(df: pd.DataFrame, py_col: str, vos_col: str) -> tuple[np.ndarray, np.ndarray, int]:
    py = pd.to_numeric(df[py_col], errors="coerce")
    vos = pd.to_numeric(df[vos_col], errors="coerce")
    mask = py.notna() & vos.notna()
    return py[mask].to_numpy(), vos[mask].to_numpy(), int(mask.sum())


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows from {INPUT_CSV.relative_to(ROOT_DIR)}")
    print(f"Columns: {list(df.columns)}\n")

    metrics = [
        ("Occurrences",        "occ_python",      "occ_vos"),
        ("TLS",                "tls_python",      "tls_vos"),
        ("Avg pub year",       "avg_year_python", "avg_year_vos"),
        ("Avg citations",      "avg_cit_python",  "avg_cit_vos"),
        ("Norm. citations",    "avg_norm_cit_python", "avg_norm_cit_vos"),
    ]

    rows: list[dict] = []
    for label, py_col, vos_col in metrics:
        if py_col not in df.columns or vos_col not in df.columns:
            print(f"  skip {label}: columns missing")
            continue
        py, vos, n = safe_pair(df, py_col, vos_col)
        if n < 4:
            print(f"  skip {label}: n={n} < 4")
            continue
        r_p, p_p = pearsonr(py, vos)
        rho_s, p_s = spearmanr(py, vos)
        ci_p_lo, ci_p_hi = fisher_z_ci(r_p, n)
        ci_s_lo, ci_s_hi = fisher_z_ci(rho_s, n)
        rows.append({
            "metric": label,
            "n": n,
            "pearson_r": round(r_p, 4),
            "pearson_ci95_lo": round(ci_p_lo, 4),
            "pearson_ci95_hi": round(ci_p_hi, 4),
            "pearson_p": p_p,
            "spearman_rho": round(rho_s, 4),
            "spearman_ci95_lo": round(ci_s_lo, 4),
            "spearman_ci95_hi": round(ci_s_hi, 4),
            "spearman_p": p_s,
        })

    out = pd.DataFrame(rows)
    n_tests = len(out)
    bonferroni_alpha = 0.05 / n_tests if n_tests else float("nan")
    out["bonferroni_alpha"] = round(bonferroni_alpha, 4)
    out["pearson_passes_bonferroni"] = out["pearson_p"] < bonferroni_alpha
    out["spearman_passes_bonferroni"] = out["spearman_p"] < bonferroni_alpha

    print(out.to_string(index=False))
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nWrote {OUTPUT_CSV.relative_to(ROOT_DIR)}")
    print(f"Bonferroni-adjusted alpha for {n_tests} simultaneous tests: {bonferroni_alpha:.4g}")


if __name__ == "__main__":
    main()
