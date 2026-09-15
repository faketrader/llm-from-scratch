"""Rebuild structural figures only; never execute a notebook or experiment.

Requires XeLaTeX and Mermaid CLI. Chromium is optional when mmdc already has
its own browser; otherwise pass --chromium /path/to/browser.
"""

from pathlib import Path
import argparse
import concurrent.futures
import json
import re
import shutil
import subprocess
import tempfile
from web_latex import group, command as replace_command

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "book/figures/theory"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", type=Path)
    parser.add_argument("--kind", choices=["all", "tikz", "mermaid"], default="all")
    parser.add_argument(
        "--referenced",
        action="store_true",
        help="Build only figures referenced by the books",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="llm-theory-figures-") as work:
        work = Path(work)
        if args.kind in ("all", "tikz"):
            sources = [
                p
                for p in sorted(SOURCE.glob("*.tex"))
                if p.name != "diagram_styles.tex"
            ]

            if args.referenced:
                names = set()
                for tex in (ROOT / "book").rglob("*.tex"):
                    text = tex.read_text()
                    for match in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?", text):
                        name, _ = group(text, match.end())
                        name = replace_command(name, "subfix", 1, lambda value: value)
                        names.add(Path(name).stem)
                sources = [
                    p
                    for p in sources
                    if p.stem in names
                    and (
                        not p.with_suffix(".pdf").exists()
                        or max(
                            p.stat().st_mtime,
                            (SOURCE / "diagram_styles.tex").stat().st_mtime,
                        )
                        > p.with_suffix(".pdf").stat().st_mtime
                    )
                ]

            def compile_tikz(source):
                result = subprocess.run(
                    [
                        "xelatex",
                        "-no-shell-escape",
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        f"-output-directory={work}",
                        source.name,
                    ],
                    cwd=SOURCE,
                    capture_output=True,
                    text=True,
                )
                log = (work / f"{source.stem}.log").read_text(errors="replace")
                if result.returncode or "Missing character:" in log:
                    raise RuntimeError(
                        f"{source.name}: compilation failed or missing glyphs\n{log[-3000:]}"
                    )
                shutil.copyfile(
                    work / f"{source.stem}.pdf", SOURCE / f"{source.stem}.pdf"
                )
                return source.name

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                for name in pool.map(compile_tikz, sources):
                    print(f"Built {name}", flush=True)
        if args.kind in ("all", "mermaid"):
            sources = sorted(SOURCE.glob("diagram-*.mmd"))
            markdown = work / "diagrams.md"
            markdown.write_text(
                "\n\n".join(f"```mermaid\n{p.read_text()}\n```" for p in sources)
            )
            command = [
                "mmdc",
                "-i",
                str(markdown),
                "-o",
                str(work / "diagrams.pdf"),
                "-f",
                "-q",
                "-c",
                str(SOURCE / "mermaid.json"),
            ]
            if args.chromium:
                config = work / "puppeteer.json"
                config.write_text(json.dumps({"executablePath": str(args.chromium)}))
                command.extend(["-p", str(config)])
            subprocess.run(command, check=True)
            for index, source in enumerate(sources, 1):
                shutil.copyfile(
                    work / f"diagrams-{index}.pdf", SOURCE / f"{source.stem}.pdf"
                )
                print(f"Built {source.name}", flush=True)


if __name__ == "__main__":
    main()
