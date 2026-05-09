"""
Multi-LLM cluster naming experiment (Phase 1 / T1.4).

Asks each model in MODELS to name and describe the 4 VOSViewer clusters
identified in `data_src/КлючовісловаКАРТА.txt`. Stores raw answers in
`bachelor_thesis/llm_naming/<vendor>__<model>.json`.

Models accessed via Ollama cloud endpoints (single API surface, multiple
vendors): DeepSeek (Pro/Flash), Qwen (3.5 397B / Coder-Next), Gemma 4,
GLM 5.1, MiniMax, Kimi K2.6 — eight independent model families.

Aggregation metrics (cosine similarity, Krippendorff α, ARI on
re-assignments) are computed in `eval_aggregate.py`.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

import ollama

from wos_parser import ROOT_DIR, load_vosviewer_map

OUTPUT_DIR = ROOT_DIR / "llm_naming"
OUTPUT_DIR.mkdir(exist_ok=True)

# Eight cloud-hosted models from six different vendors / model families.
# Order is intentional: paired by vendor so intra- and cross-vendor variation
# can be analysed separately.
MODELS: list[dict[str, str]] = [
    {"vendor": "deepseek", "id": "deepseek-v4-pro:cloud"},
    {"vendor": "deepseek", "id": "deepseek-v4-flash:cloud"},
    {"vendor": "qwen",     "id": "qwen3.5:397b-cloud"},
    {"vendor": "qwen",     "id": "qwen3-coder-next:cloud"},
    {"vendor": "google",   "id": "gemma4:31b-cloud"},
    {"vendor": "zhipu",    "id": "glm-5.1:cloud"},
    {"vendor": "minimax",  "id": "minimax-m2.7:cloud"},
    {"vendor": "moonshot", "id": "kimi-k2.6:cloud"},
]


@dataclass
class ClusterPrompt:
    cluster_id: int
    keywords: list[str]
    avg_pub_year: float
    avg_citations: float
    tls_total: float


def build_prompts() -> list[ClusterPrompt]:
    """Group VOSViewer keywords by cluster, emit one ClusterPrompt per cluster."""
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
                tls_total=float(group["tls"].sum()),
            )
        )
    return prompts


PROMPT_TEMPLATE = """You are a bibliometric analyst studying global research on
monitoring of vocational education and training (VET).

I will give you the keywords assigned to one cluster from a VOSViewer
co-occurrence map (1998 publications, Web of Science, 1997-2025). Please
respond strictly as JSON with these keys:
  "name": short cluster name (Ukrainian, <=6 words)
  "description": 1-2 sentence summary (Ukrainian)
  "methodology": dominant empirical methodology (Ukrainian, <=4 words)
  "schools": list of 2-4 research schools / dominant national contexts (English)
  "rationale": brief rationale (Ukrainian, <=2 sentences)

Output ONLY the JSON object, no markdown fence, no commentary.

Cluster #{cluster_id}
Keywords (TLS-sorted): {keywords}
Total TLS: {tls_total:.0f}
Average publication year: {avg_pub_year:.2f}
Average citations: {avg_citations:.2f}
"""


def call_ollama_cloud(model_id: str, prompt: str, *, timeout: int = 120) -> dict:
    """Call an Ollama cloud-hosted model and return parsed JSON.

    On parse failure, returns ``{"_raw": "<response text>", "_error": "<msg>"}``
    so partial data is preserved.
    """
    client = ollama.Client()
    start = time.time()
    resp = client.chat(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        format="json",
    )
    latency = time.time() - start
    raw = resp["message"]["content"]
    out: dict = {"_latency_s": round(latency, 2)}
    try:
        parsed = json.loads(raw)
        out.update(parsed)
    except Exception as exc:
        # Try to extract JSON object from possibly-fenced text
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
                out.update(parsed)
                out["_extracted_from_text"] = True
                return out
            except Exception:
                pass
        out["_error"] = f"JSON parse failed: {exc}"
        out["_raw"] = raw[:2000]
    return out


def expert_baseline() -> list[dict]:
    """Expert (author + supervisor) baseline naming of the 4 VOSViewer clusters.

    These names are taken from the analytical narrative in subsection 1.4
    and the Луганський аналітичний збірник 2025 framing. They serve as the
    reference labelling against which each LLM's interpretation is compared.
    """
    return [
        {
            "cluster_id": 1,
            "name": "Системи та політика ПТО",
            "description": (
                "Інституційний та системний вимір професійної освіти на "
                "макрорівні: порівняльні дослідження національних систем, "
                "моделі підготовки кадрів, роль роботодавців, зв'язок із "
                "вищою освітою."
            ),
            "methodology": "Порівняльний аналіз",
            "schools": ["Germany (dual)", "Switzerland (dual)", "EU policy"],
            "rationale": (
                "11 термінів, центральний vet (TLS=17857); найновіший термін "
                "company (2019.85) сигналізує про увагу до бізнесу."
            ),
        },
        {
            "cluster_id": 2,
            "name": "Емпіричні дослідження результатів навчання",
            "description": (
                "Кількісні дослідження учнів та вимірювання результатів: "
                "оцінювання, ефекти, групи, відмінності. Методологічне ядро "
                "досліджень мікрорівня."
            ),
            "methodology": "Кількісний експеримент",
            "schools": ["US empirical", "OECD assessment", "PIAAC"],
            "rationale": (
                "8 термінів, student/study як два найсильніші вузли (TLS>14000)."
            ),
        },
        {
            "cluster_id": 3,
            "name": "Педагогічна практика та компетентнісний підхід",
            "description": (
                "Мезорівень — взаємодія викладача з учнями, контекстуальне "
                "навчання, workplace learning, компетентності."
            ),
            "methodology": "Якісний контекстний аналіз",
            "schools": [
                "Workplace learning (Tynjala/Billett)",
                "Competence research (Mulder)",
            ],
            "rationale": (
                "6 термінів навколо teacher та competence; зростаюча увага до "
                "context (2019.09)."
            ),
        },
        {
            "cluster_id": 4,
            "name": "Когнітивні результати та навички",
            "description": (
                "Найменший, але семантично щільний кластер цільових результатів "
                "ПТО: skill, knowledge, problem."
            ),
            "methodology": "Когнітивне моделювання",
            "schools": ["Skills research (Rauner)", "Problem-based learning"],
            "rationale": (
                "3 терміни; функція цільового виходу системи професійної освіти."
            ),
        },
    ]


def run() -> None:
    prompts = build_prompts()
    print(f"Built {len(prompts)} cluster prompts.")

    # Save the expert baseline once.
    (OUTPUT_DIR / "_expert_baseline.json").write_text(
        json.dumps(expert_baseline(), ensure_ascii=False, indent=2)
    )

    summary: list[dict] = []
    for model in MODELS:
        out_path = OUTPUT_DIR / f"{model['vendor']}__{model['id'].replace(':', '_').replace('/', '_')}.json"
        if out_path.exists():
            print(f"  skip (cached): {out_path.name}")
            summary.append({"model": model["id"], "status": "cached"})
            continue
        results: list[dict] = []
        ok_count = 0
        print(f"\n→ {model['vendor']}/{model['id']}")
        for cp in prompts:
            prompt = PROMPT_TEMPLATE.format(
                cluster_id=cp.cluster_id,
                keywords=", ".join(cp.keywords),
                tls_total=cp.tls_total,
                avg_pub_year=cp.avg_pub_year,
                avg_citations=cp.avg_citations,
            )
            try:
                answer = call_ollama_cloud(model["id"], prompt)
                if "_error" not in answer:
                    ok_count += 1
                preview = answer.get("name", answer.get("_error", "?"))
                print(f"   cluster {cp.cluster_id}: {preview} ({answer.get('_latency_s')}s)")
            except Exception as exc:
                answer = {"_error": f"{type(exc).__name__}: {exc}"}
                print(f"   cluster {cp.cluster_id}: FAIL — {answer['_error']}")
            results.append({"cluster_id": cp.cluster_id, "answer": answer})
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"  wrote {out_path.relative_to(ROOT_DIR)} ({ok_count}/{len(prompts)} OK)")
        summary.append({"model": model["id"], "ok": ok_count, "total": len(prompts)})

    (OUTPUT_DIR / "_run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )
    print("\nDone.")


if __name__ == "__main__":
    run()
