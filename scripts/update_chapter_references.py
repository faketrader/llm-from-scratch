"""Generate chapter cross-reference metadata from the textbook order."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "book/textbook"
CHAPTER_DIR = BOOK_DIR / "chapters"
TB_ENTRY = BOOK_DIR / "textbook.tex"
OUTPUT = ROOT / "book/chapter-xrefs.generated.tex"

INCLUDE_PATTERN = re.compile(r"\\subfile\{chapters/([^{}]+\.tex)\}")
CHAPTER_PATTERN = re.compile(r"\\bookchapter\{([^{}]+)\}\{([^{}]+)\}")

included_names = INCLUDE_PATTERN.findall(TB_ENTRY.read_text())
if len(included_names) != len(set(included_names)):
    raise SystemExit("Each chapter must appear exactly once in book/textbook/textbook.tex")

chapter_paths = sorted(CHAPTER_DIR.glob("*.tex"))
known_names = {path.name for path in chapter_paths}
included_set = set(included_names)
missing = known_names - included_set
unknown = included_set - known_names
if missing or unknown:
    details = []
    if missing:
        details.append("not included: " + ", ".join(sorted(missing)))
    if unknown:
        details.append("missing files: " + ", ".join(sorted(unknown)))
    raise SystemExit("Chapter order mismatch (" + "; ".join(details) + ")")

entries = []
for number, name in enumerate(included_names, start=1):
    path = CHAPTER_DIR / name
    matches = CHAPTER_PATTERN.findall(path.read_text())
    if len(matches) != 1:
        raise SystemExit(f"Expected one two-argument \\bookchapter declaration in {path}")
    title, label = matches[0]
    entries.append((number, title, label))

labels = [label for _, _, label in entries]
if len(labels) != len(set(labels)):
    raise SystemExit("Chapter labels must be unique")

lines = ["% Generated from the chapter order in book/textbook/textbook.tex; do not edit by hand.\n"]
for number, title, label in entries:
    lines.append(f"\\bookxrefentry{{{label}}}{{{number}}}{{{title}}}\n")
text = "".join(lines)
if not OUTPUT.exists() or OUTPUT.read_text() != text:
    OUTPUT.write_text(text)
else:
    OUTPUT.touch()
print(f"Chapter cross-references: {len(entries)}")
