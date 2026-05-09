# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

Bachelor's qualifying thesis ("кваліфікаційна робота") of **Підгайко Сергій Володимирович** under supervisor **Семеріков С.О.** (КДПУ, Спеціальність 014.09 Середня освіта (Інформатика)). Topic:

> Розробка інформаційно-аналітичної системи моніторингу й аналізу освітньої діяльності закладів професійної освіти.

The repo bundles **four loosely-coupled sub-projects** that together form the thesis: a Python bibliometric pipeline, a Ukrainian LaTeX coursework draft, a TypeScript monitoring application, and reference materials. Most working sessions touch only one of them.

`context.txt` is the canonical roadmap of what lives where (in Ukrainian) — read it before reorganizing directories.

## Repo layout

```
common/              Ukrainian academic regulations (PDF + закон.txt — Закон про академічну доброчесність)
part1/
  Дані/              Web of Science exports + VOSViewer maps (data inputs for scripts/)
  Курсова/           LaTeX coursework draft (Part 1 of the thesis) — has its own CLAUDE.md
  Транскрипти/       Dated meeting/session transcripts (Ukrainian)
  Зауваження/        Photo scans of unrecognized handwritten supervisor remarks
scripts/             Python bibliometric analysis (Part 1 software)
project/             TypeScript/Fastify monitoring system (Part 2 software) — separate git repo, gitignored at root, has its own README.md
template_examples/   Two reference LaTeX thesis templates (1 = closer to КДПУ regulation, 2 = nicer style)
```

`project/` is a **nested independent git repository** (excluded by `.gitignore`). `part1/Курсова/` used to be a submodule and is now plain files in this repo.

## Sub-project: `scripts/` (Python bibliometric)

Analysis pipeline behind Chapter 1. All scripts share `wos_parser.py` (WoS plain-text parser, VOSViewer map loader, matplotlib config tuned for Ukrainian sans-serif).

Modules:
- `wos_parser.py` — shared loaders + `setup_matplotlib()`
- `descriptive_stats.py`, `text_mining.py`, `cooccurrence.py`, `clustering.py` — derived metrics
- `network_viz.py`, `overlay_viz.py`, `density_viz.py` — VOSViewer-style plots
- `comparison.py` — reconciles Python-replicated metrics against VOSViewer originals (occurrences, TLS, avg pub year, avg citations, avg normalized citations, Louvain clusters); writes CSV + LaTeX tables and prints Pearson + ARI/NMI summaries in Ukrainian

**Path caveat:** `wos_parser.py` resolves data files as `ROOT_DIR / "savedrecs.txt"` etc. (where `ROOT_DIR = repo root`). The actual data lives in `part1/Дані/`. Either symlink the inputs into the repo root, run scripts from `part1/Дані/`, or update `ROOT_DIR`/`DATA_DIR` before running. There is no `requirements.txt`; expect `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`, plus `python-louvain` (or `networkx.community`) for clustering.

Outputs are written to a `media/` directory created next to `ROOT_DIR`.

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

## Sub-project: `part1/Курсова/` (LaTeX coursework — Part 1)

Has its own `CLAUDE.md` with full LaTeX conventions (gost-numeric biblatex, biber backend, pgfplots, GOST table/figure captioning, 1.25cm indent). Build:

```bash
cd part1/Курсова
pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

`template_examples/2/` ships a `Makefile` (`make dissertation` / `make clean`) that can be cribbed if a similar build target is wanted for `Курсова/`.

## Conventions

- **Languages:** thesis prose, commit messages, transcripts, and analysis commentary are **Ukrainian**. Code, identifiers, WoS data, and bibliographic keywords are **English**. Match this when writing.
- **Academic integrity:** `common/закон.txt` is the Ukrainian Law on Academic Integrity; `common/2025 КР.pdf` is the КДПУ regulation governing thesis formatting. Cite/conform to these when in doubt about formatting or attribution.
- **Don't recurse into `project/` from the root repo for git operations** — it has its own history. Likewise don't try to commit `project/` files via the root repo (gitignored).
- **Handwritten student remarks** in `part1/Зауваження/` are JPEGs that have not been OCR'd. Treat them as opaque attachments unless explicitly asked to transcribe.
