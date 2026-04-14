#!/usr/bin/env python3
"""Check module question sections for structure, clarity, and duplication."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
QUESTION_PATTERN = re.compile(r"^(\d+)\.\s+(.*)$")
REFERENCE_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")
SPECULATION_PATTERN = re.compile(
    r"\b(maybe|perhaps|possibly|might it be|could it be|imagine if|what if)\b",
    re.I,
)

QUESTION_SECTIONS = [
    ("## 9. Observation Questions", 2, 3),
    ("## 10. Reflection Questions", 2, 3),
    ("## 11. Application Questions", 1, 2),
]


@dataclass
class ModuleQuestions:
    path: str
    title: str
    sections: Dict[str, List[str]]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-")
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


def parse_questions(section_text: str) -> Tuple[List[str], List[str]]:
    questions: List[str] = []
    errors: List[str] = []
    expected_number = 1

    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = QUESTION_PATTERN.match(line)
        if not match:
            errors.append(f"Unrecognized question line format: {line}")
            continue
        number = int(match.group(1))
        if number != expected_number:
            errors.append(f"Expected question {expected_number}, found {number}.")
            expected_number = number
        questions.append(match.group(2).strip())
        expected_number += 1

    return questions, errors


def load_module_questions(path: str) -> ModuleQuestions:
    text = Path(path).read_text(encoding="utf-8")
    title = extract_title(text)
    if not title:
        raise ValueError(f"Missing frontmatter title in {path}")

    sections: Dict[str, List[str]] = {}
    for heading, _, _ in QUESTION_SECTIONS:
        section_text = extract_section(text, heading)
        if not section_text:
            raise ValueError(f"Missing `{heading}` content in {path}")
        questions, parse_errors = parse_questions(section_text)
        if parse_errors:
            joined = "; ".join(parse_errors)
            raise ValueError(f"Invalid question numbering/format in {path} under `{heading}`: {joined}")
        sections[heading] = questions

    return ModuleQuestions(path=path, title=title, sections=sections)


def iter_markdown_files(root_path: str) -> Iterable[str]:
    if os.path.isfile(root_path):
        yield root_path
        return
    for base, _, files in os.walk(root_path):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def analyze_modules(
    root_path: str,
) -> Tuple[List[ModuleQuestions], List[str], List[Tuple[ModuleQuestions, str]]]:
    modules: List[ModuleQuestions] = []
    errors: List[str] = []
    findings: List[Tuple[ModuleQuestions, str]] = []

    for path in iter_markdown_files(root_path):
        try:
            modules.append(load_module_questions(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return modules, errors, findings

    for module in modules:
        all_questions: List[Tuple[str, str]] = []
        for heading, min_count, max_count in QUESTION_SECTIONS:
            questions = module.sections[heading]
            count = len(questions)
            if count < min_count or count > max_count:
                findings.append(
                    (
                        module,
                        f"`{heading}` has {count} question(s); expected {min_count}–{max_count}.",
                    )
                )

            for question in questions:
                if not question.endswith("?"):
                    findings.append(
                        (
                            module,
                            f"`{heading}` contains a line that does not end with `?`: {question}",
                        )
                    )

                if heading == "## 9. Observation Questions" and not REFERENCE_LINK_PATTERN.search(question):
                    findings.append(
                        (
                            module,
                            "Observation question lacks an explicit verse link/reference: " + question,
                        )
                    )

                if SPECULATION_PATTERN.search(question):
                    findings.append(
                        (
                            module,
                            f"`{heading}` contains speculative wording: {question}",
                        )
                    )

                all_questions.append((heading, question))

        seen: Dict[str, str] = {}
        for heading, question in all_questions:
            normalized = normalize_text(question)
            if normalized in seen:
                findings.append(
                    (
                        module,
                        f"Duplicate or near-duplicate question appears in `{seen[normalized]}` and `{heading}`: {question}",
                    )
                )
            else:
                seen[normalized] = heading

    return modules, errors, findings


def format_report(
    modules: Sequence[ModuleQuestions], findings: Sequence[Tuple[ModuleQuestions, str]]
) -> str:
    lines = [f"Checked {len(modules)} module question section(s)."]
    if findings:
        lines.append("")
        lines.append("Question-section findings:")
        for module, reason in findings:
            lines.append(f"- {module.title} [{module.path}]: {reason}")
    else:
        lines.append("")
        lines.append("No question-section issues found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check module question sections for structure, clarity, and duplication."
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
        help="Exit non-zero when question-section findings exist.",
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
