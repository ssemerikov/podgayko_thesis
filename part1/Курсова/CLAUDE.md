# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bibliometric research project analyzing **Vocational Education and Training (VET)** monitoring literature. Contains Web of Science citation data, keyword maps, and cluster analyses for a diploma thesis (Підгайко).

Repository: `https://github.com/ssemerikov/pidhaiko.git`

## LaTeX Coursework Structure

Based on Kharchenko's capstone template (`Kharchenko_capstone.zip`). Build with `pdflatex` + `biber`.

```
main.tex              — entry point (extarticle 14pt, a4paper)
setup.sty             — packages & formatting (geometry 3/1.5/2/2cm, babel uk/ru/en, pgfplots, GOST formatting)
scopus.bib            — Scopus bibliography entries
capstone.bib          — additional bibliography entries
chapters/
  title-page.tex      — title page (КДПУ, кафедра інформатики та прикладної математики)
  summary.tex         — abstract/summary
  vstup.tex           — introduction (ВСТУП)
  chapter1.tex        — Chapter 1: methodology
  chapter2.tex        — Chapter 2: systematic review / analysis
  chapter3.tex        — Chapter 3: results
  vysnovky.tex        — conclusions (ВИСНОВКИ)
  appendix.tex        — appendices
media/                — figures (image1.png, image2.png)
materials/            — source PDFs, scopus.csv export, supplementary docs
```

### Build commands
```bash
pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

### Key LaTeX conventions
- **biblatex** with `gost-numeric` style, `biber` backend, custom Ukrainian sorting (`abyrvalg`)
- Section titles: `\section{\MakeUppercase{...}}`; intro/conclusions as unnumbered `\section*` with `\addcontentsline`
- Charts: `pgfplots`/`tikz` bar charts, `pgf-pie` for pie charts
- Tables: numbered within sections (`\counterwithin{table}{section}`), GOST-style captions
- Figures: captioned as "Рис." with period separator
- `\citet{key}` = `\citeauthor{key}~\cite{key}` for inline author citations
- Paragraph indent: 1.25cm, line spread: 1.25
- Supervisor: Семеріков Сергій Олексійович

## Data Structure

- **`savedrecs.txt`** / **`merged_data.txt`** — Web of Science citation exports (tab-delimited Clarivate format: FN, VR, PT, AU, TI, SO, AB, DE, ID, etc.). ~1998 publications.
- **`savedrecs_1-500.txt`**, **`savedrecs_501-1000.txt`**, etc. — partitioned subsets of the same dataset.
- **`Карта.xlsx`** — keyword mapping data in Excel format.
- **`КлючовісловаКАРТА.txt`** — VOSViewer keyword map export (TSV: id, label, x, y, cluster, links, total link strength, occurrences, avg pub year, avg citations, avg normalized citations).
- **`запит_та_відповідь.txt`** — search query methodology and cluster analysis results.
- **`2025-12-03.txt`**, **`2025-12-14.txt`** — detailed AI-generated bibliometric analyses.
- **`theme`** — thematic analysis notes.

## Research Context

- **Topic**: Monitoring systems in vocational/professional education
- **Databases**: Web of Science Core Collection, ERIC, Scopus
- **Period**: 1997–2025 (emphasis on 2014–2025), English-language publications
- **Tool**: VOSViewer for bibliometric network mapping and clustering
- **4 identified clusters**: (1) VET Systems & Policy, (2) Student Outcomes, (3) Pedagogical Practice & Competence, (4) Cognitive Outcomes & Skills
- **Key metrics**: Total Link Strength (TLS), occurrences, avg citations, avg normalized citations

## Language

Analysis text is in **Ukrainian**. Citation data and keywords are in **English**. Use Ukrainian when generating analysis or commentary text.
