#!/usr/bin/env python3
"""并行编译项目 TikZ 架构图为 Notebook 可移植的 SVG。"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tqdm.auto import tqdm


@dataclass(frozen=True)
class RenderResult:
    """记录单张 TikZ 图的编译结果。"""

    source: Path
    output: Path
    ok: bool
    message: str = ""


def discover_sources(root: Path, explicit_paths: list[str]) -> list[Path]:
    """发现所有独立 TikZ 文档，排除共享样式文件。"""
    if explicit_paths:
        sources: list[Path] = []
        for raw_path in explicit_paths:
            path = (root / raw_path).resolve()
            if path.is_dir():
                sources.extend(path.glob("**/*.tex"))
            elif path.suffix == ".tex":
                sources.append(path)
        return sorted({path for path in sources if path.name != "diagram_styles.tex"})
    return sorted(
        path
        for path in (root / "assets" / "figures").glob("**/*.tex")
        if path.name != "diagram_styles.tex"
    )


def svg_is_current(source: Path, output: Path, style: Path) -> bool:
    """判断 SVG 是否存在且不早于源文件和共享样式。"""
    if not output.is_file() or output.stat().st_size < 1_000:
        return False
    svg_text = output.read_text(encoding="utf-8", errors="replace")
    if "<svg" not in svg_text or "<path" not in svg_text or "viewBox=" not in svg_text:
        return False
    output_mtime = output.stat().st_mtime_ns
    return output_mtime >= max(source.stat().st_mtime_ns, style.stat().st_mtime_ns)


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """执行编译命令并捕获诊断输出。"""
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def render_one(root: Path, source: Path) -> RenderResult:
    """使用 XeLaTeX 与 dvisvgm 原子生成单张 SVG。"""
    output = source.with_suffix(".svg")
    source_text = source.read_text(encoding="utf-8")
    if "\\def\\pgfsysdriver{pgfsys-dvisvgm.def}" not in source_text:
        return RenderResult(
            source,
            output,
            False,
            "missing required \\def\\pgfsysdriver{pgfsys-dvisvgm.def}",
        )
    with tempfile.TemporaryDirectory(prefix="my-tikz-") as temporary:
        temp_dir = Path(temporary)
        latex = run_command(
            [
                "xelatex",
                "-no-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={temp_dir}",
                str(source.relative_to(root)),
            ],
            root,
        )
        xdv = temp_dir / f"{source.stem}.xdv"
        if latex.returncode != 0 or not xdv.is_file():
            tail = "\n".join(latex.stdout.splitlines()[-30:])
            return RenderResult(source, output, False, f"XeLaTeX failed:\n{tail}")

        temporary_svg = temp_dir / f"{source.stem}.svg"
        svg = run_command(
            [
                "dvisvgm",
                "--no-fonts",
                "--exact-bbox",
                f"--output={temporary_svg}",
                str(xdv),
            ],
            root,
        )
        if svg.returncode != 0 or not temporary_svg.is_file():
            tail = "\n".join(svg.stdout.splitlines()[-30:])
            return RenderResult(source, output, False, f"dvisvgm failed:\n{tail}")

        output.parent.mkdir(parents=True, exist_ok=True)
        staging = output.with_suffix(".svg.tmp")
        shutil.copyfile(temporary_svg, staging)
        os.replace(staging, output)
    return RenderResult(source, output, True)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="可选的 TikZ 源文件或目录；默认扫描全部")
    default_root = (
        Path.cwd()
        if (Path.cwd() / "assets" / "figures" / "diagram_styles.tex").is_file()
        else Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--root", type=Path, default=default_root, help="项目根目录")
    parser.add_argument("--write", action="store_true", help="编译缺失或过期的 SVG")
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1), help="并行编译数")
    return parser.parse_args()


def main() -> int:
    """检查或并行生成全部 TikZ SVG。"""
    args = parse_args()
    root = args.root.resolve()
    style = root / "assets" / "figures" / "diagram_styles.tex"
    if not style.is_file():
        raise FileNotFoundError(style)
    sources = discover_sources(root, args.paths)
    stale = [source for source in sources if not svg_is_current(source, source.with_suffix(".svg"), style)]

    if not args.write:
        for source in stale:
            print(f"STALE {source.relative_to(root)}")
        print(f"TIKZ_SVG_AUDIT sources={len(sources)} stale={len(stale)}")
        return 1 if stale else 0

    failures: list[RenderResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
        futures = {executor.submit(render_one, root, source): source for source in stale}
        progress = tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc="阶段=编译 TikZ",
            unit="张",
        )
        for future in progress:
            result = future.result()
            if not result.ok:
                failures.append(result)
            progress.set_postfix(failed=len(failures))

    for failure in failures:
        print(f"FAILED {failure.source.relative_to(root)}\n{failure.message}")
    print(
        f"TIKZ_SVG_BUILD sources={len(sources)} rendered={len(stale) - len(failures)} "
        f"failed={len(failures)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
