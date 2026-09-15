"""Reject manually rendered reference numbers in active book and documentation sources."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (ROOT / "book",)
GENERATED = {
    ROOT / "book/chapter-xrefs.generated.tex",
    ROOT / "book/workbook/tb-numbers.generated.tex",
}

WORKBOOK_CHAPTER_DIR = ROOT / "book/workbook/chapters"
WORKBOOK_CHAPTER_CHECKS = {
    "direct workbook chapter declaration": re.compile(r"\\chapter\{"),
    "numbered workbook chapter label": re.compile(r"wb:chapter\d+"),
    "numbered workbook exercise label": re.compile(
        r"(?:q|ans):ch\d+:exercise:\d+"
    ),
    "manual workbook answer heading": re.compile(r"\\answerchapter\{"),
}

CHECKS = {
    "numbered \\bookchapter declaration": re.compile(r"\\bookchapter\{\d+\}"),
    "numbered \\answerchapter declaration": re.compile(r"\\answerchapter\{\d+\}"),
    "manually paired exercise labels": re.compile(
        r"\\exerciseitem\{[^}]+\}\{[^}]+\}"
    ),
    "legacy \\answeritem declaration": re.compile(r"\\answeritem(?:\s|\{)"),
    "hardcoded chapter reference": re.compile(r"第\s*\d+\s*章"),
    "hardcoded object reference": re.compile(
        r"(?:图|表|公式|实验|习题)\s*\d+(?:[.-]\d+)*"
    ),
    "hardcoded equation reference": re.compile(
        r"(?<!公)式\s*[（(]?\d+(?:[.-]\d+)*[）)]?"
    ),
    "numeric evidence citation": re.compile(r"(?:证据|文献|参考)\s*\[\d+\]"),
}

failures = []
paths = (
    sorted(path for directory in SOURCE_DIRS for path in directory.rglob("*.tex"))
    + sorted(path for directory in SOURCE_DIRS for path in directory.rglob("*.sty"))
    + [ROOT / "README.md"]
    + sorted(
        path
        for path in (ROOT / "docs").rglob("*.md")
    )
)
checked = 0
for path in paths:
    if path in GENERATED:
        continue
    checked += 1
    workbook_chapter = path.parent == WORKBOOK_CHAPTER_DIR
    if workbook_chapter and re.fullmatch(r"\d+\.tex", path.name):
        failures.append(
            f"{path.relative_to(ROOT)}: numeric-only workbook chapter filename"
        )
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        content = line.split("%", 1)[0] if path.suffix in {".tex", ".sty"} else line
        checks = CHECKS | (WORKBOOK_CHAPTER_CHECKS if workbook_chapter else {})
        for description, pattern in checks.items():
            if pattern.search(content):
                failures.append(
                    f"{path.relative_to(ROOT)}:{line_number}: {description}: {content.strip()}"
                )

if failures:
    raise SystemExit(
        "Hardcoded reference numbering is not allowed; use labels and reference macros:\n"
        + "\n".join(failures)
    )

print(f"Reference numbering: checked {checked} source files")
