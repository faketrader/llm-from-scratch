.DEFAULT_GOAL := textbook
TEXTBOOK_ENTRY := book/textbook/textbook.tex
CHAPTER_FILES := $(wildcard book/textbook/chapters/*.tex)
CHAPTERS := $(basename $(notdir $(CHAPTER_FILES)))
CHAPTER_TARGETS := $(addprefix chapter-,$(CHAPTERS))
FIGURE_SOURCE_DIR := book/figures/theory
DIST_DIR := dist
TEXTBOOK_BUILD_PDF := build/textbook/textbook.pdf
WORKBOOK_BUILD_PDF := build/workbook/workbook.pdf
TEXTBOOK_DIST_PDF := $(DIST_DIR)/textbook.pdf
WORKBOOK_DIST_PDF := $(DIST_DIR)/workbook.pdf
BOOK_TEX_SOURCES := $(shell find book -type f -name '*.tex')
REFERENCED_FIGURES := $(sort $(basename $(notdir $(shell grep -hEo 'figures/theory/[[:alnum:]_.-]+\.pdf' $(BOOK_TEX_SOURCES)))))
FIGURE_PDFS := $(addprefix $(FIGURE_SOURCE_DIR)/,$(addsuffix .pdf,$(REFERENCED_FIGURES)))
WEB_FIGURE_SVGS := $(addprefix $(DIST_DIR)/web/,$(addsuffix .svg,$(REFERENCED_FIGURES)))
.PHONY: figure figures web-figures textbook workbook books release chapter chapters clean --all web web-convert serve serve-web $(CHAPTER_TARGETS)
figure:
	@test -n "$(FIGURE)" || (echo 'Usage: make figure FIGURE=revision-ch08-architecture'; exit 2)
	@test "$(FIGURE)" = "$(notdir $(FIGURE))" || (echo 'FIGURE must be a filename stem, not a path'; exit 2)
	@test -f "$(FIGURE_SOURCE_DIR)/$(FIGURE).tex" || (echo 'Unknown TikZ figure'; exit 2)
	@$(MAKE) --no-print-directory "$(FIGURE_SOURCE_DIR)/$(FIGURE).pdf"
$(FIGURE_SOURCE_DIR)/%.pdf: $(FIGURE_SOURCE_DIR)/%.tex $(FIGURE_SOURCE_DIR)/diagram_styles.tex book/my-math.sty
	@mkdir -p "build/figures/$*"
	latexmk -xelatex -outdir="$(abspath build/figures/$*)" "$<"
	@if grep -Eq 'Missing character:|There were undefined references|Citation .* undefined' "build/figures/$*/$*.log"; then echo '$*: figure log contains missing glyphs or unresolved references'; exit 1; fi
	@cp "build/figures/$*/$*.pdf" "$@"
	@echo "Built $@"
figures: $(FIGURE_PDFS)
web-figures: $(WEB_FIGURE_SVGS)
$(DIST_DIR)/web/%.svg: $(FIGURE_SOURCE_DIR)/%.tex $(FIGURE_SOURCE_DIR)/diagram_styles.tex book/my-math.sty
	@mkdir -p "build/web-figures/$*" "$(DIST_DIR)/web"
	@cd "$(FIGURE_SOURCE_DIR)" && xelatex -no-pdf -interaction=nonstopmode -halt-on-error -file-line-error \
		-jobname="$*" -output-directory="$(abspath build/web-figures/$*)" \
		'\def\pgfsysdriver{pgfsys-dvisvgm.def}\AtBeginDocument{\sffamily}\input{$*.tex}'
	@if grep -Eq 'Missing character:|There were undefined references|Citation .* undefined' "build/web-figures/$*/$*.log"; then echo '$*: web figure log contains missing glyphs or unresolved references'; exit 1; fi
	dvisvgm --page=1 --no-fonts --output="$@" "build/web-figures/$*/$*.xdv"
textbook: figures
	latexmk $(TEXTBOOK_ENTRY)
	@mkdir -p "$(DIST_DIR)"
	@if ! cmp -s "$(TEXTBOOK_BUILD_PDF)" "$(TEXTBOOK_DIST_PDF)"; then cp "$(TEXTBOOK_BUILD_PDF)" "$(TEXTBOOK_DIST_PDF)"; echo "Published $(TEXTBOOK_DIST_PDF)"; fi
books: textbook workbook
release: books
workbook: textbook
	latexmk book/workbook/workbook.tex
	@mkdir -p "$(DIST_DIR)"
	@if ! cmp -s "$(WORKBOOK_BUILD_PDF)" "$(WORKBOOK_DIST_PDF)"; then cp "$(WORKBOOK_BUILD_PDF)" "$(WORKBOOK_DIST_PDF)"; echo "Published $(WORKBOOK_DIST_PDF)"; fi
chapter: figures
	@test -n "$(CHAPTER)" || (echo 'Usage: make chapter CHAPTER=14-optimization-generalization'; exit 2)
	@test -f "book/textbook/chapters/$(CHAPTER).tex" || (echo 'Unknown chapter'; exit 2)
	@printf '%s\n' $(CHAPTERS) | grep -Fxq "$(CHAPTER)" || (echo 'Chapter is not included in book/textbook/textbook.tex'; exit 2)
	@$(MAKE) --no-print-directory textbook
	@$(MAKE) --no-print-directory "chapter-$(CHAPTER)"
$(CHAPTER_TARGETS): chapter-%:
	@mkdir -p "build/chapters/$*/.biber-tmp"
	PAR_GLOBAL_TMPDIR="$(abspath build/chapters/$*/.biber-tmp)" latexmk "book/textbook/chapters/$*.tex"
chapters: textbook
	@set -e; for chapter in $(CHAPTERS); do $(MAKE) --no-print-directory chapter-$$chapter; done
web: figures web-figures web/node_modules/.my-installed
	+$(MAKE) --no-print-directory $(if $(filter -j,$(MAKEFLAGS)),,-j2) books web-convert
	node web/build.ts
web-convert: figures
	node web/convert.ts
web/node_modules/.my-installed: web/package.json web/pnpm-lock.yaml
	pnpm --dir web install --frozen-lockfile --ignore-scripts
	touch $@
serve:
	node web/serve.ts
serve-web: serve
clean:
	rm -rf -- build
ifneq ($(filter --all,$(MAKECMDGOALS)),)
	rm -rf -- dist
endif
--all:
