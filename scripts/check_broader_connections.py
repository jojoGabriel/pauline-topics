#!/usr/bin/env python3
"""Check optional broader-connections sections for references-only formatting."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\([^)]+\)")
VERSEISH_PATTERN = re.compile(r"\b[1-3]?\s?[A-Za-z]+(?:\s+[A-Za-z]+)*\s+\d+:\d+(?:[-–]\d+)?\b")


@dataclass
class ModuleConnections:
    path: str
    title: str
    section: Optional[str]


def extract_title(text: str) -> Optional[str]:
    match = TITLE_PATTERN.search(text)
    return match.group(1).strip() if match else None


def extract_section(text: str, heading: str) -> Optional[str]:
    marker = f"{heading}\n\n"
    start = text.find(marker)
    if start == -1:
        return None
    start += len(marker)
    remainder = text[start:]
    match = re.search(r"\n\n(?:---|## )", remainder)
    if match:
        remainder = remainder[: match.start()]
    section = "\n".join(line.rstrip() for line in remainder.strip().splitlines()).strip()
    return section or None


def iter_markdown_files(root_path: str) -> Iterable[str]:
    if os.path.isfile(root_path):
        yield root_path
        return
    for base, _, files in os.walk(root_path):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def load_module(path: str) -> ModuleConnections:
    text = Path(path).read_text(encoding="utf-8")
    title = extract_title(text)
    if not title:
        raise ValueError(f"Missing frontmatter title in {path}")
    section = extract_section(text, "## 12. Broader Scripture Connections (Optional)")
    return ModuleConnections(path=path, title=title, section=section)


def analyze_modules(root_path: str) -> Tuple[List[ModuleConnections], List[str], List[str]]:
    modules: List[ModuleConnections] = []
    errors: List[str] = []
    findings: List[str] = []

    for path in iter_markdown_files(root_path):
        try:
            modules.append(load_module(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return modules, errors, findings

    for module in modules:
        if not module.section:
            continue
        for line in module.section.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if not stripped.startswith("- "):
                findings.append(f"{module.title} [{module.path}]: broader-connections line is not a bullet: {stripped}")
                continue
            content = stripped[2:].strip()
            if not (LINK_PATTERN.search(content) or VERSEISH_PATTERN.search(content)):
                findings.append(f"{module.title} [{module.path}]: broader-connections entry is not a plain reference: {content}")
                continue
            if re.search(r"\b(because|shows|means|teaches|explains|therefore|so that)\b", content, re.I):
                findings.append(f"{module.title} [{module.path}]: broader-connections entry looks explanatory rather than reference-only: {content}")
                continue
            if re.search(r"[.!?]\s", content) or content.count(" ") > 8:
                findings.append(f"{module.title} [{module.path}]: broader-connections entry looks explanatory rather than reference-only: {content}")

    return modules, errors, findings


def format_report(modules: Sequence[ModuleConnections], findings: Sequence[str]) -> str:
    lines = [f"Checked {len(modules)} module broader-connections section(s)."]
    if findings:
        lines.append("")
        lines.append("Broader-connections findings:")
        for finding in findings:
            lines.append(f"- {finding}")
    else:
        lines.append("")
        lines.append("No broader-connections issues found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check broader-connections sections for references-only formatting.")
    parser.add_argument("path", nargs="?", default="modules", help="Markdown file or directory to inspect.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings exist.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    modules, errors, findings = analyze_modules(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(format_report(modules, findings))
    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
