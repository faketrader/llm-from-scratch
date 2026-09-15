.DEFAULT_GOAL := textbook
CHAPTERS := $(basename $(notdir $(wildcard book/textbook/chapters/*.tex)))
CHAPTER_XREFS := book/chapter-xrefs.generated.tex
.PHONY: figures check-references textbook workbook books release prune chapter chapters clean web serve-web
check-references:
	python3 scripts/check_reference_numbering.py
$(CHAPTER_XREFS): scripts/update_chapter_references.py book/textbook/textbook.tex $(wildcard book/textbook/chapters/*.tex)
	python3 scripts/update_chapter_references.py
figures:
	python3 scripts/build_theory_figures.py --kind tikz --referenced
textbook: figures check-references $(CHAPTER_XREFS)
	latexmk book/textbook/textbook.tex
books: textbook workbook
release: books prune
workbook: textbook
	python3 scripts/update_workbook_references.py
	latexmk book/workbook/workbook.tex
chapter: figures check-references $(CHAPTER_XREFS)
	@test -n "$(CHAPTER)" || (echo 'Usage: make chapter CHAPTER=14-optimization-generalization'; exit 2)
	@test -f "book/textbook/chapters/$(CHAPTER).tex" || (echo 'Unknown chapter'; exit 2)
	latexmk "book/textbook/chapters/$(CHAPTER).tex"
chapters: $(CHAPTER_XREFS)
	@set -e; for chapter in $(CHAPTERS); do $(MAKE) chapter CHAPTER=$$chapter; done
web:
	npm ci --prefix web --ignore-scripts --no-audit --no-fund
	python3 scripts/build_web_book.py
	python3 scripts/check_web_book.py
serve-web:
	python3 -m http.server 8765 --bind 127.0.0.1 --directory build/web
prune:
	@for directory in build/textbook build/workbook build/chapters; do if test -d "$$directory"; then find "$$directory" -type f ! -name '*.pdf' ! -name '*.synctex.gz' -delete; find "$$directory" -depth -type d -empty -delete; fi; done
clean:
	python3 -c "import shutil; shutil.rmtree('build', ignore_errors=True)"
	rm -f book/chapter-xrefs.generated.tex book/workbook/tb-numbers.generated.tex
