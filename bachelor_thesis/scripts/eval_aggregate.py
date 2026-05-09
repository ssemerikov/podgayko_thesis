"""
Aggregate metrics for the multi-LLM cluster naming experiment (T1.4).

Reads `bachelor_thesis/llm_naming/<vendor>__<model>.json` files plus the
expert baseline `_expert_baseline.json` and computes:

  1. Per-cluster cosine similarity of the «name» field's sentence embedding
     between each model and the expert baseline (sentence-transformers).
  2. Krippendorff's alpha across models for «methodology» (categorical, after
     normalisation), as a measure of inter-model agreement on dominant
     methodological framing per cluster.
  3. Pairwise Jaccard overlap of «schools» lists across models per cluster,
     as a low-noise proxy for school-attribution agreement.
  4. Per-model latency summary if `_latency_s` is recorded.

Outputs:
  - `bachelor_thesis/llm_naming/agreement_metrics.csv`     (long format)
  - `bachelor_thesis/llm_naming/agreement_summary.md`      (human-readable)
  - `bachelor_thesis/llm_naming/results_table.tex`         (LaTeX, plugged
    into rozdil1.tex via \\input{...}).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from wos_parser import ROOT_DIR

LLM_DIR = ROOT_DIR / "llm_naming"
OUT_CSV = LLM_DIR / "agreement_metrics.csv"
OUT_MD = LLM_DIR / "agreement_summary.md"
OUT_TEX = LLM_DIR / "results_table.tex"

# ---------------------------------------------------------------------------


def load_model_outputs() -> dict[str, list[dict]]:
    """Return {model_label: [cluster_record, ...]} for every json file
    except the baseline and the run summary."""
    out: dict[str, list[dict]] = {}
    for path in sorted(LLM_DIR.glob("*.json")):
        if path.stem.startswith("_") or path.name.startswith("agreement"):
            continue
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        # Three shapes are tolerated:
        #   (a) llm_cluster_naming.py  -> [{"cluster_id": N, "answer": {...}}, ...]
        #   (b) flat array w/cluster_id -> [{"cluster_id": N, ...fields}, ...]
        #   (c) flat array w/o cluster_id -> [{...}, {...}, {...}, {...}]  (positional)
        normalised: list[dict] = []
        for i, entry in enumerate(data):
            if "answer" in entry:
                rec = dict(entry["answer"])
                rec["cluster_id"] = entry.get("cluster_id", rec.get("cluster_id"))
            else:
                rec = dict(entry)
                if rec.get("cluster_id") is None:
                    rec["cluster_id"] = i + 1
            normalised.append(rec)
        out[path.stem] = normalised
    return out


def load_expert() -> list[dict]:
    p = LLM_DIR / "_expert_baseline.json"
    return json.loads(p.read_text()) if p.exists() else []


# ---------------------------------------------------------------------------
# Cosine similarity of cluster names (multilingual sentence transformer).
# ---------------------------------------------------------------------------


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def encode_names(names: list[str]):
    """Lazy import sentence-transformers to keep startup snappy."""
    from sentence_transformers import SentenceTransformer  # noqa: WPS433

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return model.encode(names, show_progress_bar=False, normalize_embeddings=True)


# ---------------------------------------------------------------------------
# Methodology categorisation (light normalisation for Krippendorff alpha).
# ---------------------------------------------------------------------------


_METHOD_CATEGORIES = {
    "qual": {"якісн", "контекст", "інтерпрет", "наратив"},
    "quant": {"кількісн", "статист", "експеримент", "емпіричн"},
    "compar": {"порівняльн", "крос", "порівнянн"},
    "biblio": {"бібліометр", "сцієнтометр", "co-citation"},
    "review": {"огляд", "сістематичн", "систематичн"},
    "case":  {"кейс", "case", "ситуац"},
    "mixed": {"змішан", "тріангул"},
    "model": {"когнітивн", "моделюв", "competence", "когнітивне моделювання"},
    "other": set(),
}


def classify_method(text: str) -> str:
    t = (text or "").lower()
    for cat, keys in _METHOD_CATEGORIES.items():
        for k in keys:
            if k in t:
                return cat
    return "other"


def krippendorff_nominal(matrix: list[list[str]]) -> float:
    """Compute Krippendorff's alpha for a list of coder × item rating lists.

    matrix[i][j] = label given by coder i to item j (string). Missing values
    are encoded as None or empty string and skipped per Krippendorff's
    standard treatment.
    """
    import krippendorff  # noqa: WPS433

    # Encode strings to integer codes.
    flat: dict[str, int] = {}
    for row in matrix:
        for v in row:
            if v in (None, ""):
                continue
            flat.setdefault(v, len(flat))
    if not flat:
        return float("nan")
    encoded: list[list] = []
    for row in matrix:
        encoded.append([flat[v] if v not in (None, "") else np.nan for v in row])
    arr = np.array(encoded, dtype=float)
    return float(krippendorff.alpha(reliability_data=arr, level_of_measurement="nominal"))


_SCHOOL_TOKEN_KEYS = (
    "german", "germany", "swiss", "switzer", "austria",
    "european", "eu ", " eu", "comparative",
    "us ", "us-", "anglo", "uk ", "british",
    "oecd", "piaac", "pisa",
    "dual", "apprent",
    "workplace", "situated", "competence", "vocational",
    "asian", "china", "japan",
    "skill", "rauner", "tynjala", "billett", "mulder",
    "problem-based", "pbl",
)


def school_tokens(items: list[str]) -> set[str]:
    """Normalise a 'schools' list to a token-bag of canonical concepts.

    Each item is lower-cased and probed for substrings of interest. The
    output captures research traditions / regions / authors regardless of
    surface form. Returns an empty set if no canonical keys match.
    """
    blob = " ".join(items or []).lower()
    return {k.strip() for k in _SCHOOL_TOKEN_KEYS if k in blob}


def jaccard(a: list[str], b: list[str]) -> float:
    """Token-bag Jaccard. Falls back to literal lower-cased Jaccard if both
    lists are non-empty but neither produces canonical tokens."""
    sa, sb = school_tokens(a), school_tokens(b)
    if not sa and not sb:
        # neither list contains canonical tokens — compare literal sets
        la = {x.lower().strip() for x in (a or [])}
        lb = {x.lower().strip() for x in (b or [])}
        if not la and not lb:
            return float("nan")
        if not la or not lb:
            return 0.0
        return len(la & lb) / len(la | lb)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# ---------------------------------------------------------------------------


def main() -> None:
    expert = load_expert()
    models = load_model_outputs()
    if not expert:
        raise SystemExit("expert baseline missing")
    if not models:
        raise SystemExit(f"no model outputs in {LLM_DIR}")

    cluster_ids = sorted({rec["cluster_id"] for rec in expert})
    expert_by_cid = {rec["cluster_id"]: rec for rec in expert}

    # 1. Cosine of cluster names.
    name_pairs: list[tuple[str, int, str]] = []  # (label, cid, text)
    for cid in cluster_ids:
        name_pairs.append(("expert", cid, expert_by_cid[cid].get("name", "")))
    for label, recs in models.items():
        by_cid = {r.get("cluster_id"): r for r in recs}
        for cid in cluster_ids:
            r = by_cid.get(cid, {})
            name_pairs.append((label, cid, r.get("name", "")))

    texts = [t for _, _, t in name_pairs]
    embeddings = encode_names(texts)
    emb_idx = {(lab, cid): i for i, (lab, cid, _) in enumerate(name_pairs)}

    rows: list[dict] = []
    for label in models:
        for cid in cluster_ids:
            sim = cosine_similarity(
                embeddings[emb_idx[("expert", cid)]],
                embeddings[emb_idx[(label, cid)]],
            )
            r = {r.get("cluster_id"): r for r in models[label]}.get(cid, {})
            rows.append(
                {
                    "model": label,
                    "cluster_id": cid,
                    "metric": "cosine_to_expert",
                    "value": round(sim, 4),
                    "lat_s": r.get("_latency_s"),
                    "model_name": r.get("name", ""),
                }
            )

    # 2. Krippendorff alpha for methodology category, per cluster.
    method_alpha: dict[int, float] = {}
    for cid in cluster_ids:
        ratings: list[list[str]] = []
        for label in models:
            r = {r.get("cluster_id"): r for r in models[label]}.get(cid, {})
            ratings.append([classify_method(r.get("methodology", ""))])
        # transpose: items=models, but we want coders=models, items=cluster
        # so for one cluster at a time we compute alpha across coders for one item — degenerate.
        # Instead compute alpha across models on the SAME item by rotating: each model is a coder,
        # each cluster is an item. Build matrix once outside the loop.
    coders = list(models)
    item_ratings = []  # rows: coders, cols: clusters
    for label in coders:
        by = {r.get("cluster_id"): r for r in models[label]}
        item_ratings.append([classify_method(by.get(cid, {}).get("methodology", "")) for cid in cluster_ids])
    method_alpha_global = krippendorff_nominal(item_ratings)

    # Per-cluster Krippendorff is degenerate (1 item) — instead compute fraction
    # of coders agreeing with the modal label.
    for cid_ix, cid in enumerate(cluster_ids):
        labels_at_cid = [item_ratings[i][cid_ix] for i in range(len(coders))]
        labels_at_cid = [x for x in labels_at_cid if x]
        if not labels_at_cid:
            method_alpha[cid] = float("nan")
            continue
        modal = max(set(labels_at_cid), key=labels_at_cid.count)
        method_alpha[cid] = labels_at_cid.count(modal) / len(labels_at_cid)
    rows.extend(
        {"model": "_aggregate", "cluster_id": cid, "metric": "method_modal_agreement",
         "value": round(method_alpha[cid], 4), "lat_s": None, "model_name": None}
        for cid in cluster_ids
    )
    rows.append({"model": "_aggregate", "cluster_id": None,
                 "metric": "method_krippendorff_alpha",
                 "value": round(method_alpha_global, 4) if not np.isnan(method_alpha_global) else None,
                 "lat_s": None, "model_name": None})

    # 3. Schools Jaccard between each model and expert, per cluster.
    for label, recs in models.items():
        by_cid = {r.get("cluster_id"): r for r in recs}
        for cid in cluster_ids:
            r = by_cid.get(cid, {})
            j = jaccard(r.get("schools", []), expert_by_cid[cid].get("schools", []))
            rows.append(
                {"model": label, "cluster_id": cid, "metric": "schools_jaccard_vs_expert",
                 "value": None if np.isnan(j) else round(j, 4), "lat_s": None,
                 "model_name": r.get("name", "")}
            )

    df = pd.DataFrame(rows)
    # Coerce cluster_id to nullable Int64 so pivot column labels match
    # cluster_ids list (avoids positional vs label mismatch in row[c]).
    df["cluster_id"] = df["cluster_id"].astype("Int64")
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"wrote {OUT_CSV.relative_to(ROOT_DIR)}  ({len(df)} rows)")

    # ---------------- Summary text + LaTeX table ---------------------------
    cos_pivot = (
        df[df.metric == "cosine_to_expert"]
        .pivot_table(index="model", columns="cluster_id", values="value")
        .round(3)
    )
    jac_pivot = (
        df[df.metric == "schools_jaccard_vs_expert"]
        .pivot_table(index="model", columns="cluster_id", values="value")
        .round(3)
    )
    cos_pivot["mean"] = cos_pivot.mean(axis=1).round(3)
    jac_pivot["mean"] = jac_pivot.mean(axis=1).round(3)

    md_lines = [
        "# Multi-LLM cluster naming agreement",
        "",
        f"Models: {len(models)}; clusters: {len(cluster_ids)}.",
        "",
        f"Krippendorff $\\alpha$ (nominal, methodology category) = "
        f"{method_alpha_global:.3f}",
        "",
        "## Cosine similarity to expert baseline (cluster name embeddings)",
        "",
        cos_pivot.to_markdown(),
        "",
        "## Schools Jaccard vs expert",
        "",
        jac_pivot.to_markdown(),
        "",
        "## Per-cluster modal-method agreement",
        "",
    ]
    for cid in cluster_ids:
        md_lines.append(f"- Cluster {cid}: {method_alpha[cid]:.2f}")
    OUT_MD.write_text("\n".join(md_lines))
    print(f"wrote {OUT_MD.relative_to(ROOT_DIR)}")

    # LaTeX results table
    tex_lines = [
        r"% Auto-generated by scripts/eval_aggregate.py — do not edit by hand.",
        r"\begin{tabular}{l" + "c" * (len(cluster_ids) + 1) + "}",
        r"\hline",
        r"\textbf{Модель} & " + " & ".join(f"К{c}" for c in cluster_ids) + r" & \textbf{Сер.} \\",
        r"\hline",
        r"\multicolumn{" + str(len(cluster_ids) + 2) + r"}{l}{\textit{Cosine similarity з~експертною назвою}} \\",
        r"\hline",
    ]
    for label, row in cos_pivot.iterrows():
        cells = [f"{row.loc[c]:.2f}" if pd.notna(row.loc[c]) else "—" for c in cluster_ids]
        tex_lines.append(
            label.replace("__", " / ").replace("_", "\\_") + " & "
            + " & ".join(cells) + f" & {row['mean']:.2f} " + r"\\"
        )
    tex_lines.append(r"\hline")
    tex_lines.append(r"\multicolumn{" + str(len(cluster_ids) + 2) + r"}{l}{\textit{Schools Jaccard з~експертною списком}} \\")
    tex_lines.append(r"\hline")
    for label, row in jac_pivot.iterrows():
        cells = [f"{row.loc[c]:.2f}" if pd.notna(row.loc[c]) else "—" for c in cluster_ids]
        tex_lines.append(
            label.replace("__", " / ").replace("_", "\\_") + " & "
            + " & ".join(cells) + f" & {row['mean']:.2f} " + r"\\"
        )
    tex_lines.append(r"\hline")
    tex_lines.append(r"\end{tabular}")
    OUT_TEX.write_text("\n".join(tex_lines))
    print(f"wrote {OUT_TEX.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
