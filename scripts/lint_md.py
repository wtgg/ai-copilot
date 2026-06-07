#!/usr/bin/env python3
"""Lint markdown files for forbidden ASCII box diagrams.

项目规则：图表必须使用 Mermaid 或 PlantUML，禁止 ASCII 框图。
允许：标准 markdown 表格（`|` 配 `---` 分隔）。

用法：
    uv run python scripts/lint_md.py                 # 扫描全部 .md
    uv run python scripts/lint_md.py path/to.md      # 扫描指定文件
    uv run python scripts/lint_md.py docs/           # 扫描指定目录
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BOX_BORDER = re.compile(r"^\+[-=]+(\+[-=]+)*\+$")
EMPTY_PIPE_ROW = re.compile(r"^\|(?:\s*\|)+\s*$")
UNICODE_BOX = re.compile(r"[┌┐└┘├┤┬┴┼─│╔╗╚╝╠╣╦╩╬═║]")
FENCE = re.compile(r"^\s*(```|~~~)")

SKIP_DIRS = {".venv", "node_modules", ".git", "__pycache__", ".pytest_cache", ".ruff_cache"}


def _classify(line: str) -> str | None:
    s = line.rstrip()
    if not s.strip():
        return None
    if BOX_BORDER.match(s):
        return "ASCII 框图边框 (+---+ / +===+)"
    if EMPTY_PIPE_ROW.match(s):
        return "空 pipe 行 (框图主体)"
    if UNICODE_BOX.search(s):
        return "Unicode 框线字符"
    return None


def lint_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="gbk")
        except Exception:
            return []
    violations: list[tuple[int, str, str]] = []
    in_block = False
    for i, raw in enumerate(text.splitlines(), 1):
        if FENCE.match(raw):
            in_block = not in_block
            continue
        if in_block:
            continue
        reason = _classify(raw)
        if reason:
            violations.append((i, raw, reason))
    return violations


def _collect(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        if t.is_file():
            files.append(t)
        elif t.is_dir():
            files.extend(
                p for p in t.rglob("*.md")
                if not any(part in SKIP_DIRS for part in p.parts)
            )
    return sorted(set(files))


def main(argv: list[str]) -> int:
    targets = [Path(p) for p in argv[1:]] if len(argv) > 1 else [Path(".")]
    files = _collect(targets)
    if not files:
        print("No markdown files to scan.", file=sys.stderr)
        return 0

    all_violations: dict[Path, list[tuple[int, str, str]]] = {}
    for f in files:
        v = lint_file(f)
        if v:
            all_violations[f] = v

    if not all_violations:
        print(f"OK: 扫描 {len(files)} 个文件，无 ASCII 框图违规")
        return 0

    total = 0
    for f, vs in all_violations.items():
        print(f"\n{f}:")
        for line_no, line, reason in vs:
            print(f"  L{line_no}: [{reason}]")
            print(f"    {line.rstrip()}")
            total += 1
    print(
        f"\n违规 {total} 处 / {len(all_violations)} 个文件。"
        "修复：用 ```mermaid 或 ```plantuml 重画。"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
