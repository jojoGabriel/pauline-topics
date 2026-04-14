#!/usr/bin/env python3
"""Run all module validators in one command."""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run quote, definition, summary, and overlap validators for Pauline Topics modules."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="modules",
        help="Markdown file or directory to inspect. Defaults to modules.",
    )
    parser.add_argument(
        "--bsb-json",
        help="Path to a local BSB JSON file or BSB USJ directory for quote validation.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Pass strict mode to the non-quote validators and return non-zero on their findings.",
    )
    parser.add_argument(
        "--quote-verbose",
        action="store_true",
        help="Pass verbose mode through to the quote validator.",
    )
    return parser


def build_commands(args: argparse.Namespace) -> List[Tuple[str, List[str]]]:
    commands: List[Tuple[str, List[str]]] = []

    quote_cmd = [sys.executable, str(SCRIPT_DIR / "validate_quotes.py"), args.path]
    if args.bsb_json:
        quote_cmd.extend(["--bsb-json", args.bsb_json])
    if args.quote_verbose:
        quote_cmd.append("--verbose")
    commands.append(("Quote validation", quote_cmd))

    definition_cmd = [sys.executable, str(SCRIPT_DIR / "check_definitions.py"), args.path]
    if args.strict:
        definition_cmd.append("--strict")
    commands.append(("Definition validation", definition_cmd))

    summary_cmd = [sys.executable, str(SCRIPT_DIR / "check_summaries.py"), args.path]
    if args.strict:
        summary_cmd.append("--strict")
    commands.append(("Summary validation", summary_cmd))

    question_cmd = [sys.executable, str(SCRIPT_DIR / "check_questions.py"), args.path]
    if args.strict:
        question_cmd.append("--strict")
    commands.append(("Question validation", question_cmd))

    overlap_cmd = [sys.executable, str(SCRIPT_DIR / "check_topic_overlap.py"), args.path]
    if args.strict:
        overlap_cmd.append("--strict")
    commands.append(("Overlap validation", overlap_cmd))

    registry_cmd = [sys.executable, str(SCRIPT_DIR / "check_registry_alignment.py"), args.path]
    if args.strict:
        registry_cmd.append("--strict")
    commands.append(("Registry validation", registry_cmd))

    volume_cmd = [sys.executable, str(SCRIPT_DIR / "check_volume_coverage.py"), args.path]
    if args.strict:
        volume_cmd.append("--strict")
    commands.append(("Volume coverage", volume_cmd))

    broader_cmd = [sys.executable, str(SCRIPT_DIR / "check_broader_connections.py"), args.path]
    if args.strict:
        broader_cmd.append("--strict")
    commands.append(("Broader connections", broader_cmd))

    question_similarity_cmd = [
        sys.executable,
        str(SCRIPT_DIR / "check_question_similarity_volume.py"),
        args.path,
    ]
    if args.strict:
        question_similarity_cmd.append("--strict")
    commands.append(("Question similarity", question_similarity_cmd))

    return commands


def run_command(label: str, command: Sequence[str]) -> int:
    print(f"== {label} ==", flush=True)
    completed = subprocess.run(command, check=False)
    print("", flush=True)
    return completed.returncode


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = build_commands(args)
    exit_code = 0
    for label, command in commands:
        return_code = run_command(label, command)
        if return_code != 0 and exit_code == 0:
            exit_code = return_code
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
