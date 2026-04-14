import importlib.util
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "validate_module_set.py"
SPEC = importlib.util.spec_from_file_location("validate_module_set", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(
    path: Path,
    title: str,
    definition: str,
    summary: str,
    quote_text: str = "For all have sinned and fall short of the glory of God.",
    module_id: str = "PT03",
) -> None:
    path.write_text(
        textwrap.dedent(
            f"""\
---
module_id: {module_id}
title: {title}
author_scope: Pauline only
text_basis: BSB
status: draft
validation_status: draft
---

# {title}
**Paul’s Teachings by Topic**
**Volume 1: Salvation and Foundations**
**A Structured Topical Study from the Letters of Paul the Apostle Using Selected Passages**
**Text Basis:** Berean Standard Bible (BSB)

---

## 1. Definition

{definition}

---

## 2. The Problem / Context

<!--
id: {module_id}-Q1
reference: Romans 3:23
source: BSB
source_url: https://biblehub.com/bsb/romans/3.htm
type: exact
ellipsis_allowed: false
-->

> "{quote_text}"
>
> *(Romans 3:23)*
> [View on Bible Hub](https://biblehub.com/bsb/romans/3.htm)

---

## 7. Summary

{summary}

---

## 8. Key Verse

<!--
id: {module_id}-Q2
reference: Romans 3:23
source: BSB
source_url: https://biblehub.com/bsb/romans/3.htm
type: exact
ellipsis_allowed: false
-->

> "For all have sinned and fall short of the glory of God."
>
> *(Romans 3:23)*
> [View on Bible Hub](https://biblehub.com/bsb/romans/3.htm)

---

## 9. Observation Questions

1. According to [Romans 3:23](https://biblehub.com/bsb/romans/3.htm), what problem do all people share?
2. What does [Romans 3:23](https://biblehub.com/bsb/romans/3.htm) say about human need?

---

## 10. Reflection Questions

1. Why does this truth matter for understanding the topic?
2. What stands out to you most here?

---

## 11. Application Questions

1. How should this truth shape the way you live?
"""
        ),
        encoding="utf-8",
    )


class ValidateModuleSetTests(unittest.TestCase):
    def test_build_commands_passes_flags_through(self):
        args = MODULE.build_parser().parse_args(
            ["modules", "--bsb-json", "bsb_usj", "--strict", "--quote-verbose"]
        )
        commands = MODULE.build_commands(args)

        self.assertEqual(len(commands), 9)
        self.assertEqual(commands[0][0], "Quote validation")
        self.assertIn("--bsb-json", commands[0][1])
        self.assertIn("bsb_usj", commands[0][1])
        self.assertIn("--verbose", commands[0][1])
        self.assertIn("--strict", commands[1][1])
        self.assertIn("--strict", commands[2][1])
        self.assertIn("--strict", commands[3][1])
        self.assertIn("--strict", commands[4][1])
        self.assertIn("--strict", commands[5][1])
        self.assertIn("--strict", commands[6][1])
        self.assertIn("--strict", commands[7][1])
        self.assertIn("--strict", commands[8][1])

    def test_cli_runs_all_checks_with_local_bsb_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03_Faith.md",
                "Faith",
                "Trusting God's promise in Christ rather than human effort.",
                "Faith receives what God promises and continues as the way believers live.",
            )

            completed = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    tmpdir,
                    "--bsb-json",
                    str(Path.cwd() / "bsb_usj"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertIn("== Quote validation ==", completed.stdout)
            self.assertIn("== Definition validation ==", completed.stdout)
            self.assertIn("== Summary validation ==", completed.stdout)
            self.assertIn("== Question validation ==", completed.stdout)
            self.assertIn("== Overlap validation ==", completed.stdout)
            self.assertIn("== Registry validation ==", completed.stdout)
            self.assertIn("== Volume coverage ==", completed.stdout)
            self.assertIn("== Broader connections ==", completed.stdout)
            self.assertIn("== Question similarity ==", completed.stdout)


if __name__ == "__main__":
    unittest.main()
