#!/usr/bin/env python3
"""Check topic definition sections for self-reference and circular dependencies."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


DEFINITION_HEADING = "## 1. Definition"
TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.M)


@dataclass
class ModuleDefinition:
    path: str
    title: str
    definition: str


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def get_opening_sentence(text: str) -> str:
    stripped = " ".join(text.strip().split())
    if not stripped:
        return ""
    match = re.split(r"(?<=[.!?])\s+", stripped, maxsplit=1)
    return match[0]


def tokenize(text: str) -> List[str]:
    normalized = normalize_text(text)
    return normalized.split() if normalized else []


def extract_title(text: str) -> Optional[str]:
    match = TITLE_PATTERN.search(text)
    return match.group(1).strip() if match else None


def extract_definition(text: str) -> Optional[str]:
    marker = f"{DEFINITION_HEADING}\n\n"
    start = text.find(marker)
    if start == -1:
        return None
    start += len(marker)
    remainder = text[start:]
    section_break = re.search(r"\n\n(?:---|## )", remainder)
    if section_break:
        remainder = remainder[: section_break.start()]
    definition = "\n".join(line.rstrip() for line in remainder.strip().splitlines()).strip()
    return definition or None


def load_module_definition(path: str) -> ModuleDefinition:
    text = Path(path).read_text(encoding="utf-8")
    title = extract_title(text)
    if not title:
        raise ValueError(f"Missing frontmatter title in {path}")
    definition = extract_definition(text)
    if not definition:
        raise ValueError(f"Missing `{DEFINITION_HEADING}` content in {path}")
    return ModuleDefinition(path=path, title=title, definition=definition)


def iter_markdown_files(root_path: str) -> Iterable[str]:
    if os.path.isfile(root_path):
        yield root_path
        return
    for base, _, files in os.walk(root_path):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def analyze_self_reference(title: str, definition: str) -> bool:
    opening = get_opening_sentence(definition)
    if not opening:
        return False

    match = re.match(r"^\s*(.+?)\s+(refers to|means|is)\s+(.+)$", opening, re.I)
    if not match:
        return False

    subject = normalize_text(match.group(1))
    predicate = normalize_text(match.group(3))
    title_stems = key_stems(title, limit=2)
    subject_stems = key_stems(subject, limit=2)
    predicate_stems = key_stems(predicate, limit=2)
    if not title_stems or not subject_stems or not predicate_stems:
        return False

    if subject_stems[0] != title_stems[0]:
        return False
    compare_len = min(len(subject_stems), len(predicate_stems), 2)
    return subject_stems[:compare_len] == predicate_stems[:compare_len]


def key_stems(text: str, limit: int = 2) -> List[str]:
    stems = []
    for token in normalize_text(text).split():
        stem = stem_token(token)
        if stem:
            stems.append(stem)
        if len(stems) >= limit:
            break
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
    }
    if token in stopwords:
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


def analyze_cross_references(
    modules: Sequence[ModuleDefinition],
) -> Tuple[Dict[str, Set[str]], Dict[Tuple[str, str], List[str]]]:
    title_map = {module.title: tokenize(module.title) for module in modules}
    adjacency: Dict[str, Set[str]] = {module.title: set() for module in modules}
    reasons: Dict[Tuple[str, str], List[str]] = {}

    for module in modules:
        definition_tokens = tokenize(module.definition)
        for other_title, title_tokens in title_map.items():
            if other_title == module.title or not title_tokens:
                continue
            if contains_phrase(definition_tokens, title_tokens):
                adjacency[module.title].add(other_title)
                reasons.setdefault((module.title, other_title), []).append(other_title)
    return adjacency, reasons


def analyze_opening_dependencies(
    modules: Sequence[ModuleDefinition],
) -> List[Tuple[ModuleDefinition, str]]:
    title_map = {module.title: tokenize(module.title) for module in modules}
    findings: List[Tuple[ModuleDefinition, str]] = []

    for module in modules:
        opening_tokens = tokenize(get_opening_sentence(module.definition))
        for other_title, title_tokens in title_map.items():
            if other_title == module.title or not title_tokens:
                continue
            if contains_phrase(opening_tokens, title_tokens):
                findings.append(
                    (
                        module,
                        f"Opening sentence leans on adjacent topic title `{other_title}` instead of defining the topic directly.",
                    )
                )
    return findings


def contains_phrase(tokens: Sequence[str], phrase_tokens: Sequence[str]) -> bool:
    if not tokens or not phrase_tokens or len(phrase_tokens) > len(tokens):
        return False
    for index in range(len(tokens) - len(phrase_tokens) + 1):
        if list(tokens[index : index + len(phrase_tokens)]) == list(phrase_tokens):
            return True
    return False


def find_cycles(adjacency: Dict[str, Set[str]]) -> List[List[str]]:
    visited: Dict[str, int] = {node: 0 for node in adjacency}
    stack: List[str] = []
    stack_set: Set[str] = set()
    cycles: Set[Tuple[str, ...]] = set()

    def canonicalize(cycle_path: List[str]) -> Tuple[str, ...]:
        nodes = cycle_path[:-1]
        rotations = []
        for i in range(len(nodes)):
            rotated = nodes[i:] + nodes[:i]
            rotations.append(tuple(rotated + [rotated[0]]))
        return min(rotations)

    def dfs(node: str) -> None:
        visited[node] = 1
        stack.append(node)
        stack_set.add(node)
        for neighbor in adjacency.get(node, set()):
            state = visited.get(neighbor, 0)
            if state == 0:
                dfs(neighbor)
            elif state == 1 and neighbor in stack_set:
                start = stack.index(neighbor)
                cycles.add(canonicalize(stack[start:] + [neighbor]))
        stack.pop()
        stack_set.remove(node)
        visited[node] = 2

    for node in adjacency:
        if visited[node] == 0:
            dfs(node)
    return [list(cycle) for cycle in sorted(cycles)]


def analyze_modules(
    root_path: str,
) -> Tuple[
    List[ModuleDefinition],
    List[str],
    List[Tuple[ModuleDefinition, str]],
    List[Tuple[ModuleDefinition, str]],
    Dict[str, Set[str]],
    List[List[str]],
]:
    modules: List[ModuleDefinition] = []
    errors: List[str] = []

    for path in iter_markdown_files(root_path):
        try:
            modules.append(load_module_definition(path))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        return modules, errors, [], [], {}, []

    self_references: List[Tuple[ModuleDefinition, str]] = []
    for module in modules:
        if analyze_self_reference(module.title, module.definition):
            self_references.append(
                (
                    module,
                    "Opening sentence repeats the topic title instead of defining it independently.",
                )
            )

    opening_dependencies = analyze_opening_dependencies(modules)
    adjacency, _ = analyze_cross_references(modules)
    cycles = find_cycles(adjacency)
    return modules, errors, self_references, opening_dependencies, adjacency, cycles


def format_report(
    modules: Sequence[ModuleDefinition],
    self_references: Sequence[Tuple[ModuleDefinition, str]],
    opening_dependencies: Sequence[Tuple[ModuleDefinition, str]],
    adjacency: Dict[str, Set[str]],
    cycles: Sequence[Sequence[str]],
) -> str:
    lines = [f"Checked {len(modules)} module definition(s)."]

    if self_references:
        lines.append("")
        lines.append("Self-referential definitions:")
        for module, reason in self_references:
            lines.append(f"- {module.title} [{module.path}]: {reason}")

    if opening_dependencies:
        lines.append("")
        lines.append("Opening-sentence topic dependencies:")
        for module, reason in opening_dependencies:
            lines.append(f"- {module.title} [{module.path}]: {reason}")

    one_way = []
    cycle_edges = set()
    for cycle in cycles:
        for index in range(len(cycle) - 1):
            cycle_edges.add((cycle[index], cycle[index + 1]))

    for source in sorted(adjacency):
        for target in sorted(adjacency[source]):
            if (source, target) not in cycle_edges:
                one_way.append((source, target))

    if cycles:
        lines.append("")
        lines.append("Circular topic-definition dependencies:")
        for cycle in cycles:
            lines.append(f"- {' -> '.join(cycle)}")

    if one_way:
        lines.append("")
        lines.append("One-way topic-definition dependencies:")
        for source, target in one_way:
            lines.append(f"- {source} -> {target}")

    if not self_references and not opening_dependencies and not cycles and not one_way:
        lines.append("")
        lines.append("No circular or self-referential definition issues found.")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check topic definition sections for self-reference and circular dependencies."
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
        help="Exit non-zero when self-reference, one-way dependencies, or cycles are found.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    modules, errors, self_references, opening_dependencies, adjacency, cycles = analyze_modules(args.path)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(format_report(modules, self_references, opening_dependencies, adjacency, cycles))

    has_findings = bool(self_references or opening_dependencies or cycles)
    if args.strict and has_findings:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
