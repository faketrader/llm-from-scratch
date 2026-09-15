"""Validate generated local links, source coverage and duplicate anchors."""

from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/web"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.errors = []
        self.exercises = 0
        self.in_article = False
        self.sections = 0
        self.figures = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article" and a.get("id") == "chapter-content":
            self.in_article = True
        if self.in_article and tag == "h2":
            self.sections += 1
        if self.in_article and tag == "figure":
            self.figures += 1
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append("Duplicate id " + a["id"])
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ["img", "script"] and a.get("src"):
            self.links.append(a["src"])
        if tag == "link" and a.get("href"):
            self.links.append(a["href"])
        if a.get("class") == "exercise":
            self.exercises += 1

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False


def main():
    pages = {}
    errors = []
    for path in OUT.glob("*.html"):
        p = Page()
        p.feed(path.read_text())
        pages[path.name] = p
        errors.extend(path.name + ": " + e for e in p.errors)
        if "@@" in path.read_text() or "LFSWEBBLOCK" in path.read_text():
            errors.append("Unexpanded placeholder " + path.name)
        if 'class="chapter-meta"' in path.read_text():
            errors.append("Unexpected heading statistics " + path.name)
    for name, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = unquote(url.path) or name
            if not (OUT / target).exists():
                errors.append(name + ": missing " + link)
                continue
            if (
                url.fragment
                and target in pages
                and unquote(url.fragment) not in pages[target].ids
            ):
                errors.append(name + ": missing anchor " + link)
    entry = (ROOT / "book/textbook/textbook.tex").read_text()
    names = re.findall(r"\\subfile\{chapters/([^}]+)\}", entry)
    for name in names:
        slug = Path(name).with_suffix(".html").name
        if slug not in pages:
            errors.append("Missing chapter " + slug)
        else:
            source = (ROOT / "book/textbook/chapters" / name).read_text()
            expected_sections = len(re.findall(r"\\section\*?\{", source))
            expected_figures = source.count(r"\begin{tikzpicture}") + source.count(
                r"\includegraphics"
            )
            if pages[slug].sections != expected_sections:
                errors.append("Section count mismatch " + slug)
            if pages[slug].figures != expected_figures:
                errors.append("Figure count mismatch " + slug)
            expected = (
                (ROOT / "book/workbook/chapters" / name)
                .read_text()
                .count(r"\exerciseitem")
            )
            if pages[slug].exercises != expected:
                errors.append("Exercise count mismatch " + slug)
    index = json.loads((OUT / "search-index.json").read_text())
    for row in index:
        u = urlsplit(row["url"])
        target = pages.get(u.path)
        if target is None or (u.fragment and unquote(u.fragment) not in target.ids):
            errors.append("Invalid search target " + row["url"])
    if errors:
        raise SystemExit("\n".join(errors[:100]))
    report = dict(
        chapters=len(names),
        pages=len(pages),
        exercises=sum(
            pages[Path(n).with_suffix(".html").name].exercises for n in names
        ),
        search_entries=len(index),
        links=sum(len(p.links) for p in pages.values()),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
