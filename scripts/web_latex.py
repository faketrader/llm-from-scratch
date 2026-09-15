"""Shared LaTeX parsing and process helpers for web publishing."""

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
OUT = ROOT / "build/web"
WORK = ROOT / "build/web-work"


def run(args, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError(
            f"{args[0]} failed:\n{result.stdout[-3000:]}\n{result.stderr[-3000:]}"
        )
    return result.stdout


def group(text, start):
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text) or text[start] != "{":
        raise ValueError(f"Expected argument at {text[start : start + 80]!r}")
    depth, index = 1, start + 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
        index += 1
    raise ValueError("Unbalanced TeX argument")


def command(text, name, nargs, replacement):
    pattern = re.compile(r"\\" + name + r"(?![A-Za-z])")
    pieces, offset = [], 0
    for match in pattern.finditer(text):
        if match.start() < offset:
            continue
        args, end = [], match.end()
        for _ in range(nargs):
            value, end = group(text, end)
            args.append(value)
        pieces.extend((text[offset : match.start()], replacement(*args)))
        offset = end
    return "".join(pieces) + text[offset:]
