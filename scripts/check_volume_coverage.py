#!/usr/bin/env python3
"""Check module coverage against a volume planning file."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
MODULE_ID_PATTERN = re.compile(r"^module_id:\s*(PT\d{2})\s*$", re.M)
VOLUME_PATTERN = re.compile(r"- \[[ x]\] V1-(\d{2}) / PT-(\d{2}) — (.+)$", re.M)


@dataclass
class ModuleRecord:
    path: str
    module_id: str
    title: str


@dataclass
class VolumeTopic:
    sequence: str
    module_id: str
    title: str


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip())


def iter_markdown_files(root_path: str) -> Iterable[str]:
    if os.path.isfile(root_path):
        yield root_path
        return
    for base, _, files in os.walk(root_path):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def load_module_record(path: str) -> ModuleRecord:
    text = Path(path).read_text(encoding="utf-8")
    module_id_match = MODULE_ID_PATTERN.search(text)
    title_match = TITLE_PATTERN.search(text)
    if not module_id_match:
        raise ValueError(f"Missing frontmatter module_id in {path}")
    if not title_match:
        raise ValueError(f"Missing frontmatter title in {path}")
    return ModuleRecord(path=path, module_id=module_id_match.group(1), title=normalize_title(title_match.group(1)))


def load_volume_plan(path: str) -> List[VolumeTopic]:
    text = Path(path).read_text(encoding="utf-8")
    topics: List[VolumeTopic] = []
    for match in VOLUME_PATTERN.finditer(text):
        topics.append(
            VolumeTopic(
                sequence=match.group(1),
                module_id=f"PT{match.group(2)}",
                title=normalize_title(match.group(3)),
            )
        )
    return topics


def analyze_modules(
    module_path: str, volume_path: str = "Volume1_Topics_FINAL.md"
) -> Tuple[List[ModuleRecord], List[str], List[str]]:
    plan = load_volume_plan(volume_path)
    plan_map = {topic.module_id: topic for topic in plan}
    modules: List[ModuleRecord] = []
    errors: List[str] = []
    findings: List[str] = []

    for path in iter_markdown_files(module_path):
        try:
            modules.append(load_module_record(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return modules, errors, findings

    module_ids = {module.module_id for module in modules}

    missing = [topic for topic in plan if topic.module_id not in module_ids]
    if missing:
        preview = ", ".join(f"V1-{topic.sequence}/{topic.module_id} {topic.title}" for topic in missing[:10])
        suffix = " ..." if len(missing) > 10 else ""
        findings.append(f"Missing planned volume topics: {preview}{suffix}")

    unexpected = [module for module in modules if module.module_id not in plan_map]
    for module in unexpected:
        findings.append(
            f"{module.title} [{module.path}]: module is present locally but not listed in {volume_path}."
        )

    return modules, errors, findings


def format_report(modules: Sequence[ModuleRecord], findings: Sequence[str]) -> str:
    lines = [f"Checked {len(modules)} module(s) against the volume plan."]
    if findings:
        lines.append("")
        lines.append("Volume-coverage findings:")
        for finding in findings:
            lines.append(f"- {finding}")
    else:
        lines.append("")
        lines.append("No volume-coverage issues found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check module coverage against a volume plan.")
    parser.add_argument("path", nargs="?", default="modules", help="Markdown file or directory to inspect.")
    parser.add_argument("--volume", default="Volume1_Topics_FINAL.md", help="Path to the volume plan file.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings exist.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    modules, errors, findings = analyze_modules(args.path, args.volume)
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
