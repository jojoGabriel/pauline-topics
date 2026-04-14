#!/usr/bin/env python3
"""Check for repeated questions across modules."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
QUESTION_PATTERN = re.compile(r"^(\d+)\.\s+(.*)$")
QUESTION_HEADINGS = [
    "## 9. Observation Questions",
    "## 10. Reflection Questions",
    "## 11. Application Questions",
]


@dataclass
class QuestionRecord:
    module_title: str
    path: str
    heading: str
    text: str


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


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


def load_questions(path: str) -> List[QuestionRecord]:
    text = Path(path).read_text(encoding="utf-8")
    title = extract_title(text)
    if not title:
        raise ValueError(f"Missing frontmatter title in {path}")
    records: List[QuestionRecord] = []
    for heading in QUESTION_HEADINGS:
        section = extract_section(text, heading)
        if not section:
            continue
        for line in section.splitlines():
            match = QUESTION_PATTERN.match(line.strip())
            if not match:
                continue
            records.append(
                QuestionRecord(
                    module_title=title,
                    path=path,
                    heading=heading,
                    text=match.group(2).strip(),
                )
            )
    return records


def analyze_modules(root_path: str) -> Tuple[List[QuestionRecord], List[str], List[str]]:
    records: List[QuestionRecord] = []
    errors: List[str] = []
    findings: List[str] = []

    for path in iter_markdown_files(root_path):
        try:
            records.extend(load_questions(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return records, errors, findings

    grouped: Dict[str, List[QuestionRecord]] = {}
    for record in records:
        normalized = normalize_text(record.text)
        if len(normalized) < 20:
            continue
        grouped.setdefault(normalized, []).append(record)

    for normalized, matches in sorted(grouped.items()):
        module_titles = sorted({match.module_title for match in matches})
        if len(module_titles) < 2:
            continue
        preview = matches[0].text
        titles = ", ".join(module_titles)
        findings.append(f"`{preview}` appears across modules: {titles}")

    return records, errors, findings


def format_report(records: Sequence[QuestionRecord], findings: Sequence[str]) -> str:
    lines = [f"Checked {len(records)} question record(s) across modules."]
    if findings:
        lines.append("")
        lines.append("Cross-module question-similarity findings:")
        for finding in findings:
            lines.append(f"- {finding}")
    else:
        lines.append("")
        lines.append("No cross-module question-similarity issues found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check for repeated questions across modules.")
    parser.add_argument("path", nargs="?", default="modules", help="Markdown file or directory to inspect.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings exist.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    records, errors, findings = analyze_modules(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(format_report(records, findings))
    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
