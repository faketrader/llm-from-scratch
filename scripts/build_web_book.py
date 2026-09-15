"""Build the static textbook and its companion exercises from existing LaTeX."""

import html
import json
import re
import shutil
import hashlib
from web_latex import ROOT, WEB, OUT, WORK, run, group, command
from html.parser import HTMLParser


class Publisher:
    def __init__(self):
        self.chapters = []
        self.registry = {}
        self.owners = {}
        self.search = []
        self.report = []
        self.terms = []
        self.citation_keys = set(
            re.findall(
                r"@\w+\s*\{\s*([^,\s]+)", (ROOT / "book/references.bib").read_text()
            )
        )
        entry = (ROOT / "book/textbook/textbook.tex").read_text()
        part = ""
        for m in re.finditer(r"\\part\{([^}]+)\}|\\subfile\{chapters/([^}]+)\}", entry):
            if m[1]:
                part = m[1]
                continue
            source = ROOT / "book/textbook/chapters" / m[2]
            text = source.read_text()
            title, label = re.search(
                r"\\bookchapter\{([^}]+)\}\{([^}]+)\}", text
            ).groups()
            ch = dict(
                number=len(self.chapters) + 1,
                title=title,
                label=label,
                part=part,
                source=source,
                slug=source.stem + ".html",
            )
            self.chapters.append(ch)
            self.registry[label] = ch
            for label in re.findall(r"\\label\{([^}]+)\}", text):
                self.owners[label] = ch
        self.numbers = dict(
            re.findall(
                r"\\newlabel\{([^}]+)\}\{\{([^}]+)\}",
                (ROOT / "build/textbook/textbook.aux").read_text(),
            )
        )

    def block(self, markup):
        token = f"LFSWEBBLOCK{len(self.blocks):05d}TOKEN"
        self.blocks[token] = markup
        return "\n\n" + token + "\n\n"

    def link(self, label, short=False, eq=False):
        owner = self.registry.get(label) or self.owners.get(label)
        if owner is None or (label not in self.registry and label not in self.numbers):
            raise ValueError("Unknown reference " + label)
        if label in self.registry:
            value = f"第{owner['number']}章" + (
                "" if short else "《" + owner["title"] + "》"
            )
            url = owner["slug"]
        else:
            value = self.numbers[label]
            value = "(" + value + ")" if eq else value
            url = owner["slug"] + "#" + label
        return r"\href{" + url + "}{" + value + "}"

    def math(self, m):
        env, body = m[1], m[2]
        anchors = []
        # Split align rows only outside nested matrix/cases environments.
        rows = []
        start = 0
        depth = 0
        if env == "align":
            for token in re.finditer(r"\\begin\{[^}]+\}|\\end\{[^}]+\}|\\\\", body):
                if token[0].startswith(r"\begin"):
                    depth += 1
                elif token[0].startswith(r"\end"):
                    depth -= 1
                elif depth == 0:
                    rows.append(body[start : token.start()])
                    start = token.end()
        rows.append(body[start:])
        for i, row in enumerate(rows):
            labels = re.findall(r"\\label\{([^}]+)\}", row)
            if r"\notag" not in row and r"\nonumber" not in row:
                self.eq += 1
                number = f"{self.ch['number']}.{self.eq}"
                for label in labels:
                    if self.numbers.get(label) != number:
                        raise ValueError(
                            f"Equation drift {label}: {number} != {self.numbers.get(label)}"
                        )
                row += r"\tag{" + number + "}"
            for label in labels:
                anchors.append('<span id="' + html.escape(label) + '"></span>')
            rows[i] = re.sub(r"\\label\{[^}]+\}", "", row)
        body = r"\\".join(rows)
        tex = (
            r"\[" + body + r"\]"
            if env == "equation"
            else r"\begin{align}" + body + r"\end{align}"
        )
        return self.block(
            "".join(anchors)
            + '<div class="math display">'
            + html.escape(tex)
            + "</div>"
        )

    def figure(self, m):
        text = m[0]
        self.fig += 1
        tikz = re.search(r"\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}", text)
        if tikz:
            colors = "\n".join(
                re.findall(
                    r"\\definecolor\{[^}]+\}\{[^}]+\}\{[^}]+\}",
                    (ROOT / "book/mybook.sty").read_text(),
                )
            )
            tex = "\n".join(
                [
                    r"\documentclass[tikz,border=8pt]{standalone}",
                    r"\usepackage{ctex,amsmath,amssymb}",
                    r"\usetikzlibrary{calc,positioning,arrows.meta,shapes.geometric,decorations.pathreplacing,patterns}",
                    r"\newcommand{\Real}{\mathbb{R}}",
                    r"\newcommand{\dif}{\mathop{}\!\mathrm{d}}",
                    r"\DeclareMathOperator{\softmax}{softmax}",
                    r"\begin{document}",
                    tikz[0],
                    r"\end{document}",
                ]
            )
            if "LFS" in tikz[0]:
                tex = tex.replace(
                    r"\begin{document}", colors + "\n" + r"\begin{document}"
                )
        else:
            image = re.search(
                r"\\includegraphics(?:\[[^\]]*\])?\{\\subfix\{([^}]+)\}\}", text
            )
            if not image:
                raise ValueError("Unrecognized figure " + text[:100])
            path = (self.ch["source"].parent / image[1]).resolve().with_suffix(".tex")
            tex = path.read_text()
            tex = command(
                tex, "input", 1, lambda name: (path.parent / name).read_text()
            )
        caption = re.search(r"\\captionof\{figure\}|\\caption(?:\[[^\]]*\])?", text)
        numbered = caption is not None
        caption, _ = group(text, caption.end()) if numbered else ("", 0)
        label = re.search(r"\\label\{([^}]+)\}", text)
        num = f"{self.ch['number']}.{self.fig}"
        if label and self.numbers.get(label[1]) != num:
            raise ValueError("Figure drift " + label[1])
        name = f"{self.ch['source'].stem}-figure-{self.fig}"
        svg = OUT / (name + ".svg")
        texpath = WORK / (name + ".tex")
        svgsource = r"\def\pgfsysdriver{pgfsys-dvisvgm.def}" + "\n" + tex
        if not svg.exists() or not texpath.exists() or texpath.read_text() != svgsource:
            texpath.write_text(svgsource)
            run(
                [
                    "xelatex",
                    "-no-pdf",
                    "-no-shell-escape",
                    "-halt-on-error",
                    "-interaction=nonstopmode",
                    texpath.name,
                ],
                cwd=WORK,
            )
            if "Missing character:" in texpath.with_suffix(".log").read_text():
                raise ValueError("Missing figure glyph " + name)
            run(
                [
                    "dvisvgm",
                    "--no-fonts",
                    "--output=" + str(svg),
                    str(texpath.with_suffix(".xdv")),
                ]
            )
        ident = label[1] if label else name
        caption_html = run(
            ["pandoc", "-f", "latex", "-t", "html5", "--mathjax", "--wrap=none"],
            input=caption,
        ).strip()
        caption_html = re.sub(r"^<p>|</p>$", "", caption_html)
        caption_html = f"图 {num}　{caption_html}" if numbered else ""
        alt = caption or f"{self.ch['title']}结构图{self.fig}"
        return self.block(
            f'<figure id="{ident}"><img src="{name}.svg" alt="{html.escape(alt)}" loading="lazy"><figcaption>{caption_html}</figcaption></figure>'
        )

    def prepare(self, text, body=False):
        text = re.sub(r"(?<!\\)%[^\n]*", "", text)
        if body:
            if r"\begin{document}" in text:
                text = text.split(r"\begin{document}", 1)[1].split(
                    r"\end{document}", 1
                )[0]
            text = command(text, "bookchapter", 2, lambda *_: "")
            text = text.replace(r"\chapterreferences", "")
            # Float and center wrappers containing graphics become semantic figures.
            text = re.sub(
                r"\\begin\{(center|figure)\}(?:\[[^\]]*\])?[\s\S]*?\\end\{\1\}",
                lambda m: self.figure(m)
                if r"\begin{tikzpicture}" in m[0] or r"\includegraphics" in m[0]
                else m[0],
                text,
            )
            text = re.sub(
                r"\\begin\{(equation|align)\}([\s\S]*?)\\end\{\1\}", self.math, text
            )

        def term(zh, en, ab):
            value = r"\textbf{" + zh + "}（" + en + ("，" + ab if ab else "") + "）"
            if body:
                ident = "term-" + str(len(self.terms) + 1)
                self.terms.append(
                    dict(zh=zh, en=en, abbr=ab, url=self.ch["slug"] + "#" + ident)
                )
                value = r"\hypertarget{" + ident + "}{}" + value
            return value

        text = command(text, "term", 3, term)
        text = command(text, "keyconcept", 1, lambda x: r"\textbf{" + x + "}")
        text = command(text, "num", 1, lambda x: f"{int(x):,}" if x.isdigit() else x)
        text = command(text, "bookcode", 1, lambda x: r"\texttt{" + x + "}")
        text = command(text, "bookmargin", 1, lambda x: r"\emph{" + x + "}")
        text = command(
            text,
            "qty",
            2,
            lambda x, u: x
            + " "
            + u.replace(r"\milli\second", "ms").replace(r"\giga\byte", "GB"),
        )
        text = command(text, "bookxref", 1, lambda x: self.link(x))
        text = re.sub(
            r"(\\href\{[^}]+\}\{第\d+章《[^》]+》\})\[([^\]]*)\]", r"\1\2", text
        )
        text = command(text, "bookxrefshort", 1, lambda x: self.link(x, short=True))
        for name in ["eqref", "ref", "tbobject", "tbnumberref"]:
            text = command(
                text, name, 1, lambda x, n=name: self.link(x, eq=n == "eqref")
            )

        def box(m):
            title = (
                m[2]
                or {
                    "bookassumptions": "假设与适用范围",
                    "bookinsight": "结论",
                    "bookalgorithm": "计算过程",
                }[m[1]]
            )
            if m[1] == "bookalgorithm":
                self.alg += 1
                title = f"算法{self.ch['number']}.{self.alg}　" + title
            return r"\begin{quote}\textbf{" + title + "}\n\n"

        text = re.sub(
            r"\\begin\{(bookassumptions|bookinsight|bookalgorithm)\}(?:\[([^\]]*)\])?",
            box,
            text,
        )
        text = re.sub(
            r"\\end\{(?:bookassumptions|bookinsight|bookalgorithm)\}",
            r"\\end{quote}",
            text,
        )

        def table_caption(title):
            self.table += 1
            return (
                r"\textbf{表 " + f"{self.ch['number']}.{self.table}　" + title + "}\n\n"
            )

        text = command(text, "captionof", 2, lambda kind, title: table_caption(title))
        text = command(text, "caption", 1, table_caption)
        text = text.replace(r"\optional", r"\textit{（选修）}").replace(
            r"\phantomsection", ""
        )
        return command(text, "label", 1, lambda x: r"\hypertarget{" + x + "}{}")

    def render(self, text):
        ast = json.loads(run(["pandoc", "-f", "latex", "-t", "json"], input=text))

        def inspect(v):
            if isinstance(v, dict):
                if v.get("t") == "Cite":
                    for citation in v["c"][0]:
                        if citation["citationId"] not in self.citation_keys:
                            raise ValueError(
                                "Unknown citation " + citation["citationId"]
                            )
                    inspect(v["c"][0])
                    return
                if v.get("t") in ["RawInline", "RawBlock"]:
                    raise ValueError("Unsupported LaTeX " + str(v))
                for x in v.values():
                    inspect(x)
            elif isinstance(v, list):
                for x in v:
                    inspect(x)

        inspect(ast)
        result = run(
            [
                "pandoc",
                "-f",
                "json",
                "-t",
                "html5",
                "--mathjax",
                "--wrap=none",
                "--citeproc",
                "--bibliography=" + str(ROOT / "book/references.bib"),
                "-M",
                "link-citations=true",
                "-M",
                "lang=zh-CN",
            ],
            input=json.dumps(ast),
        )
        for token, markup in self.blocks.items():
            result = result.replace("<p>" + token + "</p>", markup)
        if "LFSWEBBLOCK" in result:
            raise ValueError("Unexpanded block")
        return re.sub(
            r"(<table\b[\s\S]*?</table>)", r'<div class="table-scroll">\1</div>', result
        )

    def publish(self, ch):
        self.ch = ch
        self.eq = self.fig = self.alg = self.table = 0
        self.blocks = {}
        content = self.render(self.prepare(ch["source"].read_text(), body=True))
        refs = re.search(r'<div id="refs"[\s\S]*', content)
        bibliography = ""
        if refs:
            bibliography = refs[0]
            foot = bibliography.find("<section")
            tail = bibliography[foot:] if foot >= 0 else ""
            bibliography = bibliography[:foot] if foot >= 0 else bibliography
            content = content[: refs.start()] + tail
        toc = []

        def heading(m):
            num = f"{ch['number']}.{len(toc) + 1}"
            toc.append(f'<li><a href="#{m[1]}"><span>{num}</span>{m[2]}</a></li>')
            return (
                f'<h2 id="{m[1]}"><span class="section-number">{num}</span>{m[2]}</h2>'
            )

        for old, new in [(4, 5), (3, 4), (2, 3)]:
            content = re.sub(r"<(/?)h" + str(old) + r"\b", r"<\1h" + str(new), content)
        content = re.sub(r'<h1 id="([^"]+)">([\s\S]*?)</h1>', heading, content)

        def unnumbered_heading(m):
            toc.append(f'<li><a href="#{m[1]}">{m[2]}</a></li>')
            return f'<h2 class="unnumbered" id="{m[1]}">{m[2]}</h2>'

        content = re.sub(
            r'<h1 class="unnumbered" id="([^"]+)">([\s\S]*?)</h1>',
            unnumbered_heading,
            content,
        )
        answers = []
        wb = ROOT / "book/workbook/chapters" / ch["source"].name
        for i, item in enumerate(wb.read_text().split(r"\exerciseitem")[1:], 1):
            q, a = item.split(r"\begin{workbookanswers}", 1)
            a = a.split(r"\end{workbookanswers}", 1)[0]
            optional = r"\optional" in q
            q = q.replace(r"\optional", "")
            answers.append(
                f'<div class="exercise" id="exercise-{i}"><div class="exercise-heading">习题 {ch["number"]}.{i}'
                + ('<span class="optional">选修</span>' if optional else "")
                + "</div>"
                + self.render(self.prepare(q))
                + '<details><summary>展开参考解析</summary><div class="answer">'
                + self.render(self.prepare(a))
                + "</div></details></div>"
            )
        passage = 0

        def anchor(m):
            nonlocal passage
            passage += 1
            tag, attrs = m[1], m[2]
            if "id=" not in attrs:
                attrs += f' id="passage-{passage}"'
            return "<" + tag + attrs + ">"

        content = re.sub(r"<(p|h2|h3)(\s[^>]*|)>", anchor, content)
        answers = [re.sub(r"<(p|h2|h3)(\s[^>]*|)>", anchor, a) for a in answers]
        template = (WEB / "reader.html").read_text()
        for asset in ("reader.css", "reader.js"):
            version = hashlib.sha256((WEB / asset).read_bytes()).hexdigest()[:12]
            template = template.replace(f'"{asset}"', f'"{asset}?v={version}"')
        template = (
            template.replace("注意力机制", html.escape(ch["title"]))
            .replace("CHAPTER 05", f"CHAPTER {ch['number']:02d}")
            .replace(">05<", f">{ch['number']:02d}<")
            .replace("Attention", "")
        )
        template = template.replace("语言模型理论基础", ch["part"]).replace(
            "第一篇 · ", ""
        )
        template = template.replace("attention.pdf", "textbook.pdf")
        for key, value in {
            "TOC": "<ol>" + "".join(toc) + "</ol>",
            "CONTENT": content,
            "ANSWERS": "".join(answers),
            "REFERENCES": bibliography,
        }.items():
            template = template.replace("@@" + key + "@@", value)
        booknav = (
            '<details class="all-book-chapters"><summary>全书章节</summary>'
            + self.booknav(ch)
            + "</details>"
        )
        template = template.replace(
            '<nav aria-label="本章目录">',
            '<a class="all-chapters-link" href="index.html">← 全书目录</a>'
            + booknav
            + '<div class="chapter-nav-label">本章目录</div><nav aria-label="本章目录">',
        )
        n = ch["number"]
        pager = '<div class="chapter-pager">'
        if n > 1:
            prev = self.chapters[n - 2]
            pager += f'<a href="{prev["slug"]}">← {prev["title"]}</a>'
        else:
            pager += "<span></span>"
        if n < len(self.chapters):
            nxt = self.chapters[n]
            pager += f'<a href="{nxt["slug"]}">{nxt["title"]} →</a>'
        template = template.replace("<footer>", pager + "</div><footer>")
        template = template.replace("第5章", "第" + str(ch["number"]) + "章").replace(
            "输入术语或正文关键词，如：因果掩码", "输入术语或正文关键词，如：注意力"
        )
        template = template.replace("搜索本章", "搜索全书").replace(
            "搜索正文、习题与解析", "搜索全书正文、习题与解析"
        )
        (OUT / ch["slug"]).write_text(template)
        parser = SearchParser(ch["slug"], ch["title"])
        parser.feed(content + "<section>" + "".join(answers) + "</section>")
        self.search.extend(parser.entries)
        self.report.append(
            dict(
                chapter=n,
                title=ch["title"],
                sections=len(toc),
                figures=self.fig,
                equations=self.eq,
                exercises=len(answers),
                sha256=hashlib.sha256(ch["source"].read_bytes()).hexdigest(),
            )
        )
        print(f"{n:02d} {ch['title']}: {self.fig} figures", flush=True)

    def booknav(self, current=None):
        groups = []
        part = ""
        for ch in self.chapters:
            if ch["part"] != part:
                if part:
                    groups.append("</ol></details>")
                part = ch["part"]
                opened = " open" if current is None or current["part"] == part else ""
                groups.append(
                    f'<details class="book-part"{opened}><summary>{part}</summary><ol>'
                )
            active = ' class="current" aria-current="page"' if current == ch else ""
            groups.append(
                f'<li><a href="{ch["slug"]}"{active}><span>{ch["number"]:02d}</span>{ch["title"]}</a></li>'
            )
        groups.append("</ol></details>")
        return (
            '<div class="book-navigation">'
            + "".join(groups)
            + '</div><div class="book-extras"><a href="preface.html">前言</a><a href="reading-guide.html">阅读说明</a><a href="notation.html">符号与数学约定</a><a href="terms.html">中英文术语索引</a></div>'
        )


class SearchParser(HTMLParser):
    def __init__(self, url, title):
        super().__init__()
        self.entries = []
        self.url = url
        self.title = title
        self.buff = None
        self.index = 0
        self.tag = None

    def handle_starttag(self, tag, attrs):
        if tag in ["p", "h2", "h3"] and self.buff is None:
            self.buff = []
            self.tag = tag
            self.ident = dict(attrs).get("id", "")

    def handle_data(self, data):
        if self.buff is not None:
            self.buff.append(data)

    def handle_endtag(self, tag):
        if tag == self.tag and self.buff is not None:
            text = "".join(self.buff).strip()
            if text:
                self.entries.append(
                    dict(
                        url=self.url + ("#" + self.ident if self.ident else ""),
                        title=self.title,
                        text=text,
                    )
                )
            self.buff = None
            self.tag = None


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    run(["make", "books"], cwd=ROOT)
    p = Publisher()
    for ch in p.chapters:
        p.publish(ch)
    for name in ["reader.css", "reader.js"]:
        shutil.copy2(WEB / name, OUT / name)
    for src, dest in [("mathjax", "mathjax"), ("@mathjax/mathjax-newcm-font", "fonts")]:
        shutil.copytree(
            WEB / "node_modules" / src, OUT / "vendor" / dest, dirs_exist_ok=True
        )
    shutil.copy2(ROOT / "build/textbook/textbook.pdf", OUT / "textbook.pdf")
    shutil.copy2(ROOT / "build/workbook/workbook.pdf", OUT / "workbook.pdf")
    (OUT / "search-index.json").write_text(json.dumps(p.search, ensure_ascii=False))
    # Landing uses the same reader shell and a full five-part table of contents.
    page = (OUT / p.chapters[0]["slug"]).read_text()
    start = page.index('<main id="chapter">')
    end = page.index("</main>", start) + len("</main>")
    landing = (
        '<main id="chapter"><div class="chapter-heading"><div class="eyebrow">LLM FROM SCRATCH</div><h1>大语言模型</h1><p class="chapter-subtitle">从理论到实践</p></div><article id="chapter-content"><p>从基本运算与数学机制出发，建立模型、训练、推理与应用系统之间的完整联系。</p><div class="home-links"><a href="'
        + p.chapters[0]["slug"]
        + '">开始阅读 →</a><a href="textbook.pdf">教材 PDF ↗</a><a href="workbook.pdf">习题 PDF ↗</a></div><h2>全书目录</h2>'
        + p.booknav()
        + "</article><footer>大语言模型：从理论到实践</footer></main>"
    )
    page = page[:start] + landing + page[end:]
    page = page.replace("<title>绪论 ·", "<title>全书目录 ·")

    def clean_extra(shell, title):
        shell = re.sub(r'<nav aria-label="本章目录">[\s\S]*?</nav>', "", shell)
        shell = re.sub(
            r'<div class="chapter-current">[\s\S]*?</div>',
            '<div class="chapter-current"><strong>' + title + "</strong></div>",
            shell,
        )
        shell = re.sub(
            r'<div class="sidebar-bottom">[\s\S]*?</div>',
            '<div class="sidebar-bottom"><a href="textbook.pdf">教材 PDF ↗</a><a href="workbook.pdf">习题 PDF ↗</a></div>',
            shell,
        )
        shell = shell.replace('<div class="chapter-nav-label">本章目录</div>', "")
        shell = re.sub(r'<a href="#exercises">[\s\S]*?</a>', "", shell)
        return shell

    page = clean_extra(page, "全书目录")
    (OUT / "index.html").write_text(page)

    def extra_page(slug, title, content):
        shell = (OUT / p.chapters[0]["slug"]).read_text()
        a = shell.index('<main id="chapter">')
        b = shell.index("</main>", a) + len("</main>")
        main = (
            '<main id="chapter"><div class="chapter-heading"><div class="eyebrow">大语言模型：从理论到实践</div><h1>'
            + title
            + '</h1></div><article id="chapter-content">'
            + content
            + '</article><footer><a href="index.html">返回全书目录</a></footer></main>'
        )
        shell = shell[:a] + main + shell[b:]
        shell = clean_extra(shell, title)
        shell = re.sub(
            r"<title>.*?</title>", "<title>" + title + " · 大语言模型</title>", shell
        )
        (OUT / slug).write_text(shell)

    p.ch = p.chapters[0]
    p.blocks = {}
    p.eq = p.fig = p.alg = p.table = 0
    for name, title in [
        ("preface", "前言"),
        ("reading-guide", "阅读说明"),
        ("notation", "符号与数学约定"),
    ]:
        text = (ROOT / "book/textbook/frontmatter" / (name + ".tex")).read_text()
        text = re.sub(r"\\chapter\*\{[^}]+\}", "", text)
        text = command(text, "addcontentsline", 3, lambda *_: "")
        text = p.prepare(text)
        content = p.render(text)
        for old, new in [(3, 4), (2, 3), (1, 2)]:
            content = re.sub(r"<(/?)h" + str(old) + r"\b", r"<\1h" + str(new), content)
        extra_page(name + ".html", title, content)
    unique = {}
    for term in p.terms:
        unique.setdefault((term["zh"], term["en"]), term)
    rows = []
    for term in sorted(unique.values(), key=lambda t: t["en"].casefold()):
        rows.append(
            '<tr><td><a href="'
            + term["url"]
            + '">'
            + html.escape(term["zh"])
            + "</a></td><td>"
            + html.escape(term["en"])
            + "</td><td>"
            + html.escape(term["abbr"])
            + "</td></tr>"
        )
    extra_page(
        "terms.html",
        "中英文术语索引",
        '<div class="table-scroll"><table><tr><th>中文</th><th>英文</th><th>缩写</th></tr>'
        + "".join(rows)
        + "</table></div>",
    )
    (WORK / "book-manifest.json").write_text(
        json.dumps(p.report, ensure_ascii=False, indent=2)
    )
    print("Published", len(p.chapters), "chapters")


if __name__ == "__main__":
    main()
