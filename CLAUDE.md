# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

Bachelor's qualifying thesis ("кваліфікаційна робота") of **Підгайко Сергій Володимирович** under supervisor **Семеріков С.О.** (КДПУ, Спеціальність 014.09 Середня освіта (Інформатика)). Topic:

> Розробка інформаційно-аналітичної системи моніторингу й аналізу освітньої діяльності закладів професійної освіти.

The repo bundles **four loosely-coupled sub-projects** that together form the thesis: a Python bibliometric pipeline, a Ukrainian LaTeX coursework draft, a TypeScript monitoring application, and reference materials. Most working sessions touch only one of them.

`context.txt` is the canonical roadmap of what lives where (in Ukrainian) — read it before reorganizing directories.

## Repo layout

```
bachelor_thesis/     Working directory for the qualifying thesis. All edits go here.
  main.tex           Single buildable document — includes both розділи
  setup.sty          Times New Roman (tempora), DSTU-style geometry, fancyhdr
  *.bib              capstone.bib, scopus.bib (will grow to 70–90 entries)
  chapters/          title-page, integrity, summary, vstup, rozdil1, rozdil2, vysnovky, appendix
    _legacy_part1/   Archived pre-refactor chapter stubs (kept for content migration)
  media/             Vector PDF figures only (matplotlib output)
  scripts/           Adapted Python pipeline + LLM cluster naming + perf benchmarks
  data/              Derived artifacts (thesaurus, prior_reviews.csv)
  data_src           symlink → ../part1/Дані/  (raw WoS + VOSViewer inputs)
  llm_naming/        Multi-LLM cluster naming experiment outputs (Phase 1 / T1.4)
common/              Ukrainian academic regulations (PDF + закон.txt — Закон про академічну доброчесність)
part1/
  Дані/              Web of Science exports + VOSViewer maps (read-only inputs)
  Курсова/           Original LaTeX coursework draft — READ-ONLY (do not edit)
  Транскрипти/       Dated meeting/session transcripts (Ukrainian)
  Зауваження/        Handwritten supervisor remarks (JPGs) + transcribed.md
scripts/             Original Python bibliometric pipeline — READ-ONLY (working copies live in bachelor_thesis/scripts/)
project/             TypeScript/Fastify monitoring system (Part 2 prototype) — READ-ONLY, separate git repo, gitignored at root
template_examples/   Reference LaTeX thesis templates — READ-ONLY
BACKLOG.md           Aggregated TODO log: supervisor remarks + RQ + phase tasks
```

`project/` is a **nested independent git repository** (excluded by `.gitignore`). `part1/Курсова/` used to be a submodule and is now plain files in this repo.

**Hard editing constraints (per supervisor 2026-05-09):**
- ❌ Do **not** edit `part1/Курсова/**` — original draft is preserved as-is.
- ❌ Do **not** edit `project/**` — prototype is consumed read-only as a black box.
- ❌ `scripts/`, `common/`, `template_examples/` are also read-only sources.
- ✅ All thesis editing happens in `bachelor_thesis/**`.

**LaTeX figure convention:** TikZ figures live **inline in the chapter `.tex` files**, never in a separate `figures/` directory. Do not create `\input{figures/foo.tex}` patterns.

## Sub-project: `scripts/` (frozen Python bibliometric pipeline) — READ-ONLY

Original analysis pipeline behind Chapter 1. **Working copies live in `bachelor_thesis/scripts/`** with paths fixed and additional scripts (LLM cluster naming, expert-eval aggregator, perf benchmarks). Do not edit the originals.

Reference for what each module does:
- `wos_parser.py` — shared loaders + `setup_matplotlib()`
- `descriptive_stats.py`, `text_mining.py`, `cooccurrence.py`, `clustering.py` — derived metrics
- `network_viz.py`, `overlay_viz.py`, `density_viz.py` — VOSViewer-style plots
- `comparison.py` — Python-vs-VOSViewer reconciliation, CSV + LaTeX export, Pearson + ARI/NMI summaries in Ukrainian

In `bachelor_thesis/scripts/wos_parser.py` the path bug is fixed: `DATA_DIR = ROOT_DIR / "data_src"` resolves through the symlink to `part1/Дані/`. Use that copy. Dependencies pinned in `bachelor_thesis/scripts/requirements.txt`.

## Sub-project: `project/` (TypeScript / Fastify monolith)

Modular monolith on Node.js 20 / Fastify 4 / TypeScript / PostgreSQL 16 / Redis 7 (EJS + htmx + Alpine on the client, BullMQ workers, Drizzle ORM). It is a **separate git repository** — open it as its own working directory (`cd project`) when doing real work there; the root repo does not track its files.

Detailed setup, scripts, and a chronological phase log are in `project/README.md`. Quick reference:

```bash
cd project
nvm use && npm install
docker compose up -d              # postgres :5432, redis :6379, mailhog :1025/:8025
npm run db:migrate && npm run db:seed
npm run dev                       # http://localhost:3000
npm test                          # vitest (testcontainers spin up Postgres)
npm run test:e2e                  # playwright + axe-core
npm run lint && npm run typecheck
```

Single test: `npx vitest run path/to/file.test.ts -t "name"`.

Architectural shape — every data module under `src/modules/<name>/` follows the same skeleton: `schema.ts` (Drizzle) · `repository.ts` · `validators.ts` (Zod) · `service.ts` (idempotent compare-then-write + audit) · `routes.ts` · `excel.ts` (xlsx template + worker) · `views/` (EJS). Cross-cutting concerns live in `src/shared/{config, db, auth, queue, excel, views, i18n, mail, logging}`. Audit log is append-only with a SHA-256 hash chain; ABAC (`src/modules/abac/`) is JSON-AST policy with deny-overrides default-deny, Redis-cached with pub/sub invalidation. lefthook runs eslint + prettier + typecheck pre-commit and `npm test` pre-push.

When extending a data module, mirror the existing pattern (staff / facilities / students / professions / enrollment_dynamics / projects / transparency / quality) — `project/README.md` lists the per-phase tasks that produced each one.

## Sub-project: `bachelor_thesis/` (working LaTeX — Parts 1 + 2)

Active working directory. Mirrors `part1/Курсова/` skeleton but adds new chapters (`chapter4_implications.tex`, `chapter_displaced.tex`, `chapter_war_recovery.tex`) and the entirely new `part2/` chapter. Build via the supplied Makefile:

```bash
cd bachelor_thesis
make            # builds both main.pdf (Part 1) and part2/main.pdf (Part 2)
make main       # Part 1 only
make part2      # Part 2 only
make clean
```

Bibliography migrates to **DSTU 8302:2015** (currently `gost-numeric` as a near-equivalent technical proxy; replace in Phase 1 / T1.6). Body font: **Times New Roman 14pt** via `tempora`, 1.5 line spacing, margins **30/10/20/20 mm** (left/right/top/bottom per Положення КДПУ §6), page numbers in the **upper-right corner**, hyphenation disabled (`\hyphenpenalty=10000`).

**Document structure (per Положення КДПУ §4):** rigid 2-розділ layout — Розділ 1 = бібліометрика + теоретичні засади, Розділ 2 = система + евалюація. Top-level structure: `title-page → integrity (Додаток В affidavit) → summary → ToC → vstup → rozdil1 → rozdil2 → vysnovky → bibliography → appendix`. Висновки до розділу — наприкінці кожного rozdil. **Do not** split into more than 2 розділи; subordinate content goes into subsections (1.1, 1.2, 2.1, 2.2, …). Old per-chapter stubs are archived in `bachelor_thesis/chapters/_legacy_part1/`.

**GenAI disclosure** belongs in the «Методи дослідження» subsection of `vstup.tex`, not as a standalone declaration.

**Tire convention:** in Ukrainian academic style, write `~-- ` (non-breaking space + en-dash + space) literally in source. Never write ` -- ` with a regular leading space. Example: `Кривий Ріг~-- 2026`.

**Figure convention:** vector only (PDF / TikZ inline). PNG is forbidden. matplotlib scripts in `bachelor_thesis/scripts/` are configured with `savefig.format='pdf'`. For Розділ 2, **data-schema and ABAC policy visualisations follow the JSON Crack approach** (https://jsoncrack.com/) — node-graph layouts implemented inline via TikZ; do not embed external images.

Detailed plan: `~/.claude/plans/crispy-soaring-swing.md`. Open punch list with all supervisor remarks: `BACKLOG.md`. Transcribed handwritten remarks: `part1/Зауваження/transcribed.md`.

## Sub-project: `part1/Курсова/` (frozen reference — Part 1 draft)

Has its own `CLAUDE.md` with original LaTeX conventions. **Do not edit** — kept as a frozen reference snapshot. The original Makefile-style build still works for diff/comparison purposes:

```bash
cd part1/Курсова
pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

## Conventions

- **Languages:** thesis prose, commit messages, transcripts, and analysis commentary are **Ukrainian**. Code, identifiers, WoS data, and bibliographic keywords are **English**. Match this when writing.
- **Regulatory floor:** the only VET law cited as currently in force is **Закон України «Про професійну освіту» №4574-IX** ([zakon.rada.gov.ua/laws/show/4574-20](https://zakon.rada.gov.ua/laws/show/4574-20)). The 1998 «Про професійно-технічну освіту» is mentioned only in historical retrospectives. Source priority: 2025–2026 publications.
- **Reform drivers** to thread through both parts: (a) wartime needs (oborona retraining, evacuated institutions), (b) post-war reconstruction (veterans, IDPs, critical professions), (c) EU harmonization (EU4Skills, ETF, EQAVET, Copenhagen process). The displaced-institutions case (Луганщина) is a recurring concrete example.
- **TikZ figures inline only.** Do not create `bachelor_thesis/**/figures/` directories; place TikZ pictures directly in the chapter `.tex` files where they appear.
- **Academic integrity:** `common/закон.txt` is the Ukrainian Law on Academic Integrity (№4742-IX); `common/2025 КР.pdf` is the КДПУ regulation governing thesis formatting. Cite/conform.
- **Don't recurse into `project/` from the root repo for git operations** — it has its own history. Likewise don't try to commit `project/` files via the root repo (gitignored). Treat it as a black-box system under test: HTTP API, Postgres, BullMQ; benchmarks live in `bachelor_thesis/scripts/`.
- **Handwritten supervisor remarks** in `part1/Зауваження/` are JPEGs. Transcription is in `part1/Зауваження/transcribed.md` with a punch-list of 14 numbered items + per-page edits.
