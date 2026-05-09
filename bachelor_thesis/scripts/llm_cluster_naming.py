"""
Multi-LLM cluster naming experiment (Phase 1 / T1.4).

Reads the 4 VOSViewer clusters identified in `data_src/КлючовісловаКАРТА.txt`,
prompts each model in MODELS to (a) name the cluster, (b) describe it in 1–2
sentences, (c) identify dominant methodology and (d) leading research schools.
Stores raw answers in `bachelor_thesis/llm_naming/<model>.json`.

Aggregation metrics (cosine similarity, Krippendorff α, ARI on re-assignments)
are computed in `eval_aggregate.py` (separate file) — this script only collects
raw responses to keep failure modes localised.

Status: skeleton. Wiring of providers (Anthropic, Ollama, OpenRouter) and
prompt templates is intentionally left as TODO and will be completed when
T1.4 is picked up.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from wos_parser import DERIVED_DIR, ROOT_DIR, load_vosviewer_map

OUTPUT_DIR = ROOT_DIR / "llm_naming"
OUTPUT_DIR.mkdir(exist_ok=True)

# Three Claude tiers via Anthropic, plus open-weight models via Ollama and
# OpenRouter. Adjust as access becomes available.
MODELS: list[dict[str, str]] = [
    {"vendor": "anthropic", "id": "claude-haiku-4-5"},
    {"vendor": "anthropic", "id": "claude-sonnet-4-6"},
    {"vendor": "anthropic", "id": "claude-opus-4-7"},
    {"vendor": "ollama", "id": "llama3.1:8b"},
    {"vendor": "ollama", "id": "qwen2.5:32b"},
    {"vendor": "ollama", "id": "gemma2:27b"},
    {"vendor": "openrouter", "id": "mistralai/mistral-large"},
]


@dataclass
class ClusterPrompt:
    cluster_id: int
    keywords: list[str]
    avg_pub_year: float
    avg_citations: float


def build_prompts() -> list[ClusterPrompt]:
    """Group VOSViewer keywords by cluster and emit one prompt per cluster."""
    df = load_vosviewer_map()
    prompts: list[ClusterPrompt] = []
    for cluster_id, group in df.groupby("cluster"):
        group = group.sort_values("tls", ascending=False)
        prompts.append(
            ClusterPrompt(
                cluster_id=int(cluster_id),
                keywords=group["label"].tolist(),
                avg_pub_year=float(group["avg_pub_year"].mean()),
                avg_citations=float(group["avg_citations"].mean()),
            )
        )
    return prompts


PROMPT_TEMPLATE = """You are a bibliometric analyst studying global research on
monitoring of vocational education and training (VET).

I will give you the keywords assigned to one cluster from a VOSViewer
co-occurrence map (1998 publications, Web of Science, 1997–2025), together
with descriptive statistics. Please respond strictly as JSON with the keys:
  - "name": short cluster name (Ukrainian, ≤6 words)
  - "description": 1–2 sentence summary (Ukrainian)
  - "methodology": the dominant empirical methodology (Ukrainian, ≤4 words)
  - "schools": list of 2–4 research schools / dominant national contexts
  - "rationale": brief rationale (Ukrainian, ≤2 sentences)

Cluster #{cluster_id}
Keywords (TLS-sorted): {keywords}
Average publication year: {avg_pub_year:.2f}
Average citations: {avg_citations:.2f}
"""


def call_anthropic(model_id: str, prompt: str) -> dict:
    # TODO[T1.4]: wire anthropic.Anthropic client; respect ANTHROPIC_API_KEY.
    raise NotImplementedError("Anthropic call not wired yet")


def call_ollama(model_id: str, prompt: str) -> dict:
    # TODO[T1.4]: use ollama.chat(...) with format='json'.
    raise NotImplementedError("Ollama call not wired yet")


def call_openrouter(model_id: str, prompt: str) -> dict:
    # TODO[T1.4]: POST https://openrouter.ai/api/v1/chat/completions.
    raise NotImplementedError("OpenRouter call not wired yet")


def call_model(model: dict, prompt: str) -> dict:
    if model["vendor"] == "anthropic":
        return call_anthropic(model["id"], prompt)
    if model["vendor"] == "ollama":
        return call_ollama(model["id"], prompt)
    if model["vendor"] == "openrouter":
        return call_openrouter(model["id"], prompt)
    raise ValueError(f"Unknown vendor: {model['vendor']}")


def run() -> None:
    prompts = build_prompts()
    print(f"Built {len(prompts)} cluster prompts.")
    for model in MODELS:
        results = []
        for cp in prompts:
            prompt = PROMPT_TEMPLATE.format(
                cluster_id=cp.cluster_id,
                keywords=", ".join(cp.keywords),
                avg_pub_year=cp.avg_pub_year,
                avg_citations=cp.avg_citations,
            )
            try:
                answer = call_model(model, prompt)
            except NotImplementedError as exc:
                answer = {"error": str(exc)}
            results.append({"cluster_id": cp.cluster_id, "answer": answer})
        out_path = OUTPUT_DIR / f"{model['vendor']}_{model['id'].replace('/', '_')}.json"
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"  wrote {out_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    run()
