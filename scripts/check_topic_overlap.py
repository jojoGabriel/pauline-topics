#!/usr/bin/env python3
"""Check modules for likely overlap via duplicate key verses and very similar prose."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
SECTION_BREAK_PATTERN = re.compile(r"\n\n(?:---|## )")
REFERENCE_PATTERN = re.compile(r"^reference:\s*(.+?)\s*$", re.M)


@dataclass
class ModuleOverlap:
    path: str
    title: str
    definition: str
    summary: str
    key_reference: str
    illustration_references: List[str]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> List[str]:
    normalized = normalize_text(text)
    return normalized.split() if normalized else []


def significant_stems(text: str) -> Set[str]:
    stems = set()
    for token in tokenize(text):
        stem = stem_token(token)
        if stem:
            stems.add(stem)
    return stems


def stem_token(token: str) -> str:
    stopwords = {
        "the",
        "a",
        "an",
        "to",
        "of",
        "and",
        "with",
        "by",
        "in",
        "through",
        "god",
        "be",
        "being",
        "been",
        "is",
        "are",
        "was",
        "were",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "as",
        "for",
        "from",
        "into",
        "now",
        "then",
        "their",
        "them",
        "they",
        "who",
        "what",
        "where",
        "when",
        "why",
        "how",
        "all",
        "people",
        "believers",
        "christ",
        "jesus",
        "paul",
        "letters",
        "teaches",
        "teaching",
    }
    if token in stopwords or token.isdigit():
        return ""
    stem = token
    if stem.endswith("ification") and len(stem) > 11:
        return stem[: -9] + "ify"
    if stem.endswith("ified") and len(stem) > 7:
        return stem[: -5] + "ify"
    for suffix in ("ation", "ition", "ness", "ment", "ity", "ing", "ied", "ed", "es", "s"):
        if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
            stem = stem[: -len(suffix)]
            break
    if stem.endswith("i") and len(stem) > 3:
        stem = stem[:-1] + "y"
    return stem


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


def extract_key_reference(text: str) -> Optional[str]:
    section = extract_section(text, "## 8. Key Verse")
    if not section:
        return None
    match = REFERENCE_PATTERN.search(section)
    return match.group(1).strip() if match else None


def extract_references_from_section(text: str, heading: str) -> List[str]:
    section = extract_section(text, heading)
    if not section:
        return []
    return [match.strip() for match in REFERENCE_PATTERN.findall(section)]


def load_module_overlap(path: str) -> ModuleOverlap:
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
    key_reference = extract_key_reference(text)
    if not key_reference:
        raise ValueError(f"Missing key verse metadata reference in {path}")
    illustration_references = extract_references_from_section(text, "## 5. Illustration / Example")
    return ModuleOverlap(
        path=path,
        title=title,
        definition=definition,
        summary=summary,
        key_reference=key_reference,
        illustration_references=illustration_references,
    )


def iter_markdown_files(root_path: str) -> Iterable[str]:
    if os.path.isfile(root_path):
        yield root_path
        return
    for base, _, files in os.walk(root_path):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def jaccard_similarity(left: Set[str], right: Set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def analyze_modules(
    root_path: str,
) -> Tuple[List[ModuleOverlap], List[str], List[str], List[str], List[str], List[str]]:
    modules: List[ModuleOverlap] = []
    errors: List[str] = []

    for path in iter_markdown_files(root_path):
        try:
            modules.append(load_module_overlap(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return modules, errors, [], [], [], []

    duplicate_key_verses: List[str] = []
    duplicate_illustrations: List[str] = []
    similar_definitions: List[str] = []
    similar_summaries: List[str] = []

    references: Dict[str, List[ModuleOverlap]] = {}
    for module in modules:
        references.setdefault(module.key_reference, []).append(module)
    for reference, grouped in sorted(references.items()):
        if len(grouped) > 1:
            titles = ", ".join(sorted(module.title for module in grouped))
            duplicate_key_verses.append(f"{reference}: {titles}")

    illustration_refs: Dict[str, List[ModuleOverlap]] = {}
    for module in modules:
        for reference in module.illustration_references:
            illustration_refs.setdefault(reference, []).append(module)
    for reference, grouped in sorted(illustration_refs.items()):
        unique_titles = sorted({module.title for module in grouped})
        if len(unique_titles) > 1:
            duplicate_illustrations.append(f"{reference}: {', '.join(unique_titles)}")

    for index, left in enumerate(modules):
        for right in modules[index + 1 :]:
            definition_score = jaccard_similarity(
                significant_stems(left.definition), significant_stems(right.definition)
            )
            if definition_score >= 0.6:
                similar_definitions.append(
                    f"{left.title} <-> {right.title} (similarity {definition_score:.2f})"
                )

            summary_score = jaccard_similarity(
                significant_stems(left.summary), significant_stems(right.summary)
            )
            if summary_score >= 0.65:
                similar_summaries.append(
                    f"{left.title} <-> {right.title} (similarity {summary_score:.2f})"
                )

    return modules, errors, duplicate_key_verses, duplicate_illustrations, similar_definitions, similar_summaries


def format_report(
    modules: Sequence[ModuleOverlap],
    duplicate_key_verses: Sequence[str],
    duplicate_illustrations: Sequence[str],
    similar_definitions: Sequence[str],
    similar_summaries: Sequence[str],
) -> str:
    lines = [f"Checked {len(modules)} module overlap candidate(s)."]
    if duplicate_key_verses:
        lines.append("")
        lines.append("Duplicate key verse references:")
        for finding in duplicate_key_verses:
            lines.append(f"- {finding}")
    if duplicate_illustrations:
        lines.append("")
        lines.append("Duplicate illustration/example references:")
        for finding in duplicate_illustrations:
            lines.append(f"- {finding}")
    if similar_definitions:
        lines.append("")
        lines.append("Highly similar definitions:")
        for finding in similar_definitions:
            lines.append(f"- {finding}")
    if similar_summaries:
        lines.append("")
        lines.append("Highly similar summaries:")
        for finding in similar_summaries:
            lines.append(f"- {finding}")
    if not duplicate_key_verses and not duplicate_illustrations and not similar_definitions and not similar_summaries:
        lines.append("")
        lines.append("No major overlap findings found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check modules for duplicate key verses and unusually similar prose."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="modules",
        help="Markdown file or directory to inspect. Defaults to modules.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when overlap findings exist.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    modules, errors, duplicate_key_verses, duplicate_illustrations, similar_definitions, similar_summaries = analyze_modules(
        args.path
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        format_report(
            modules,
            duplicate_key_verses,
            duplicate_illustrations,
            similar_definitions,
            similar_summaries,
        )
    )
    if args.strict and (duplicate_key_verses or duplicate_illustrations or similar_definitions or similar_summaries):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
