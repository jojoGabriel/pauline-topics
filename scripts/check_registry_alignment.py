#!/usr/bin/env python3
"""Check module files against the canonical topics registry."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)
MODULE_ID_PATTERN = re.compile(r"^module_id:\s*(PT\d{2})\s*$", re.M)
REGISTRY_PATTERN = re.compile(r"- \[[ x]\] PT-(\d{2}) (.+)$", re.M)


@dataclass
class ModuleRecord:
    path: str
    filename: str
    module_id: str
    title: str


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip())


def registry_id_to_module_id(registry_id: str) -> str:
    return f"PT{registry_id}"


def expected_filename(module_id: str, title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    return f"{module_id}_{slug}.md"


def extract_registry(path: str) -> Dict[str, str]:
    text = Path(path).read_text(encoding="utf-8")
    registry: Dict[str, str] = {}
    for match in REGISTRY_PATTERN.finditer(text):
        module_id = registry_id_to_module_id(match.group(1))
        registry[module_id] = normalize_title(match.group(2))
    return registry


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
    return ModuleRecord(
        path=path,
        filename=Path(path).name,
        module_id=module_id_match.group(1),
        title=normalize_title(title_match.group(1)),
    )


def analyze_modules(
    module_path: str, registry_path: str = "topics.md"
) -> Tuple[List[ModuleRecord], List[str], List[str]]:
    registry = extract_registry(registry_path)
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

    seen_ids: Dict[str, str] = {}
    for module in modules:
        if module.module_id not in registry:
            findings.append(
                f"{module.title} [{module.path}]: module_id `{module.module_id}` is not present in topics.md."
            )
            continue

        expected_title = registry[module.module_id]
        if module.title != expected_title:
            findings.append(
                f"{module.title} [{module.path}]: frontmatter title does not match topics.md (`{expected_title}`)."
            )

        expected_name = expected_filename(module.module_id, expected_title)
        if module.filename != expected_name:
            findings.append(
                f"{module.title} [{module.path}]: filename should be `{expected_name}`."
            )

        if module.module_id in seen_ids:
            findings.append(
                f"{module.title} [{module.path}]: duplicate module_id `{module.module_id}` also used by {seen_ids[module.module_id]}."
            )
        else:
            seen_ids[module.module_id] = module.path

    return modules, errors, findings


def format_report(modules: Sequence[ModuleRecord], findings: Sequence[str]) -> str:
    lines = [f"Checked {len(modules)} module registry record(s)."]
    if findings:
        lines.append("")
        lines.append("Registry-alignment findings:")
        for finding in findings:
            lines.append(f"- {finding}")
    else:
        lines.append("")
        lines.append("No registry-alignment issues found.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check modules against topics.md.")
    parser.add_argument("path", nargs="?", default="modules", help="Markdown file or directory to inspect.")
    parser.add_argument("--registry", default="topics.md", help="Path to the canonical topics registry.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings exist.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    modules, errors, findings = analyze_modules(args.path, args.registry)
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
