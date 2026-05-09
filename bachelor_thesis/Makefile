# Makefile for compiling Підгайко's bachelor's qualifying thesis
# (адаптовано з template_examples/2/Makefile)
#
# Usage:
#   make            - Compile main.pdf (Part 1 + integrated structure)
#   make part2      - Compile part2/main.pdf (system development chapter)
#   make all        - Build both PDFs
#   make clean      - Remove auxiliary files
#   make clean-all  - Remove auxiliary files and PDFs

.PHONY: all main part2 clean clean-all help

LATEX_FLAGS = -interaction=nonstopmode -shell-escape

all: main part2

main: main.pdf

main.pdf: main.tex setup.sty *.bib chapters/*.tex
	pdflatex $(LATEX_FLAGS) main.tex ; \
	biber main && \
	pdflatex $(LATEX_FLAGS) main.tex && \
	pdflatex $(LATEX_FLAGS) main.tex

part2: part2/main.pdf

part2/main.pdf: part2/main.tex setup.sty
	cd part2 && \
	pdflatex $(LATEX_FLAGS) main.tex ; \
	biber main && \
	pdflatex $(LATEX_FLAGS) main.tex && \
	pdflatex $(LATEX_FLAGS) main.tex

clean:
	rm -f *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.fls *.fdb_latexmk
	rm -f part2/*.aux part2/*.bbl part2/*.bcf part2/*.blg part2/*.log
	rm -f part2/*.out part2/*.run.xml part2/*.toc part2/*.fls part2/*.fdb_latexmk

clean-all: clean
	rm -f main.pdf part2/main.pdf

help:
	@echo "Targets:"
	@echo "  make / make all   - Build both main.pdf and part2/main.pdf"
	@echo "  make main         - Build main.pdf (Part 1 + integrated thesis)"
	@echo "  make part2        - Build part2/main.pdf (Part 2 chapter)"
	@echo "  make clean        - Remove aux files"
	@echo "  make clean-all    - Remove aux files + PDFs"
