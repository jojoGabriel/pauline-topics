#!/usr/bin/env python3
"""Check summary sections for drift away from module definitions."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
SECTION_BREAK_PATTERN = re.compile(r"\n\n(?:---|## )")


@dataclass
class ModuleSummary:
    path: str
    title: str
    definition: str
    summary: str


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> List[str]:
    normalized = normalize_text(text)
    return normalized.split() if normalized else []


def get_opening_sentence(text: str) -> str:
    stripped = " ".join(text.strip().split())
    if not stripped:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", stripped, maxsplit=1)
    return parts[0]


def contains_phrase(tokens: Sequence[str], phrase_tokens: Sequence[str]) -> bool:
    if not tokens or not phrase_tokens or len(phrase_tokens) > len(tokens):
        return False
    for index in range(len(tokens) - len(phrase_tokens) + 1):
        if list(tokens[index : index + len(phrase_tokens)]) == list(phrase_tokens):
            return True
    return False


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
    match = SECTION_BREAK_PATTERN.search(remainder)
    if match:
        remainder = remainder[: match.start()]
    section = "\n".join(line.rstrip() for line in remainder.strip().splitlines()).strip()
    return section or None


def load_module_summary(path: str) -> ModuleSummary:
    text = Path(path).read_text(encoding="utf-8")
    title = extract_title(text)
    if not title:
        raise ValueError(f"Missing frontmatter title in {path}")
    definition = extract_section(text, "## 1. Definition")
    if not definition:
        raise ValueError(f"Missing `## 1. Definition` content in {path}")
    summary = extract_section(text, "## 7. Summary")
    if not summary:
        raise ValueError(f"Missing `## 7. Summary` content in {path}")
    return ModuleSummary(path=path, title=title, definition=definition, summary=summary)


def iter_markdown_files(root_path: str) -> Iterable[str]:
    if os.path.isfile(root_path):
        yield root_path
        return
    for base, _, files in os.walk(root_path):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def extract_topic_mentions(
    text: str,
    title_map: Dict[str, List[str]],
    exclude_title: str,
    min_title_tokens: int = 1,
) -> Set[str]:
    tokens = tokenize(text)
    mentions: Set[str] = set()
    for title, title_tokens in title_map.items():
        if title == exclude_title or not title_tokens or len(title_tokens) < min_title_tokens:
            continue
        if contains_phrase(tokens, title_tokens):
            mentions.add(title)
    return mentions


def analyze_modules(
    root_path: str,
) -> Tuple[List[ModuleSummary], List[str], List[Tuple[ModuleSummary, str]]]:
    modules: List[ModuleSummary] = []
    errors: List[str] = []

    for path in iter_markdown_files(root_path):
        try:
            modules.append(load_module_summary(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return modules, errors, []

    title_map = {module.title: tokenize(module.title) for module in modules}
    findings: List[Tuple[ModuleSummary, str]] = []

    for module in modules:
        summary_opening_mentions = extract_topic_mentions(
            get_opening_sentence(module.summary), title_map, module.title, min_title_tokens=2
        )
        if summary_opening_mentions:
            joined = ", ".join(sorted(summary_opening_mentions))
            findings.append(
                (
                    module,
                    f"Summary opening leans on adjacent topic title(s): {joined}.",
                )
            )

        definition_mentions = extract_topic_mentions(
            module.definition, title_map, module.title, min_title_tokens=2
        )
        summary_mentions = extract_topic_mentions(
            module.summary, title_map, module.title, min_title_tokens=2
        )
        added_mentions = sorted(summary_mentions - definition_mentions)
        if added_mentions:
            findings.append(
                (
                    module,
                    "Summary introduces neighboring topic title(s) not present in the definition: "
                    + ", ".join(added_mentions)
                    + ".",
                )
            )

    return modules, errors, findings


def format_report(modules: Sequence[ModuleSummary], findings: Sequence[Tuple[ModuleSummary, str]]) -> str:
    lines = [f"Checked {len(modules)} module summary section(s)."]
    if findings:
        lines.append("")
        lines.append("Summary alignment findings:")
        for module, reason in findings:
            lines.append(f"- {module.title} [{module.path}]: {reason}")
    else:
        lines.append("")
        lines.append("No summary-alignment issues found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check summary sections for drift from module definitions.")
    parser.add_argument(
        "path",
        nargs="?",
        default="modules",
        help="Markdown file or directory to inspect. Defaults to modules.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when summary-alignment findings exist.",
    )
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
