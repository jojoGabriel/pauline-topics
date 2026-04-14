import importlib.util
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_questions.py"
SPEC = importlib.util.spec_from_file_location("check_questions", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(
    path: Path,
    title: str,
    observation: str,
    reflection: str,
    application: str,
    application_heading: str = "## 11. Application Questions",
) -> None:
    path.write_text(
        textwrap.dedent(
            f"""\
---
module_id: PTXX
title: {title}
---

# {title}

---

## 1. Definition

Placeholder definition.

---

## 9. Observation Questions

{observation}

---

## 10. Reflection Questions

{reflection}

---

{application_heading}

{application}
"""
        ),
        encoding="utf-8",
    )


class CheckQuestionsTests(unittest.TestCase):
    def test_clean_questions_are_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "1. According to [Romans 1:16–17](https://biblehub.com/bsb/romans/1.htm), what does the gospel reveal?\n2. What do [Romans 4:16](https://biblehub.com/bsb/romans/4.htm) and [Ephesians 2:8](https://biblehub.com/bsb/ephesians/2.htm) show about faith?",
                "1. Why is faith contrasted with works?\n2. What stands out to you about living by faith?",
                "1. How should faith shape the way you rely on God?",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(findings, [])

    def test_missing_application_section_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "1. According to [Romans 1:16–17](https://biblehub.com/bsb/romans/1.htm), what does the gospel reveal?\n2. What do [Romans 4:16](https://biblehub.com/bsb/romans/4.htm) and [Ephesians 2:8](https://biblehub.com/bsb/ephesians/2.htm) show about faith?",
                "1. Why is faith contrasted with works?\n2. What stands out to you about living by faith?",
                "1. How should faith shape the way you rely on God?",
                application_heading="## 11. Application Question",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(len(errors), 1)
            self.assertIn("Missing `## 11. Application Questions` content", errors[0])
            self.assertEqual(findings, [])

    def test_observation_question_without_reference_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "1. What does Paul say about faith?\n2. What do [Romans 4:16](https://biblehub.com/bsb/romans/4.htm) and [Ephesians 2:8](https://biblehub.com/bsb/ephesians/2.htm) show about faith?",
                "1. Why is faith contrasted with works?\n2. What stands out to you about living by faith?",
                "1. How should faith shape the way you rely on God?",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)
            self.assertIn("Observation question lacks an explicit verse link/reference", findings[0][1])

    def test_speculative_language_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "1. According to [Romans 1:16–17](https://biblehub.com/bsb/romans/1.htm), what does the gospel reveal?\n2. What do [Romans 4:16](https://biblehub.com/bsb/romans/4.htm) and [Ephesians 2:8](https://biblehub.com/bsb/ephesians/2.htm) show about faith?",
                "1. Perhaps Paul means something more here?\n2. What stands out to you about living by faith?",
                "1. How should faith shape the way you rely on God?",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)
            self.assertIn("contains speculative wording", findings[0][1])

    def test_duplicate_questions_are_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = "How should faith shape the way you rely on God?"
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "1. According to [Romans 1:16–17](https://biblehub.com/bsb/romans/1.htm), what does the gospel reveal?\n2. What do [Romans 4:16](https://biblehub.com/bsb/romans/4.htm) and [Ephesians 2:8](https://biblehub.com/bsb/ephesians/2.htm) show about faith?",
                f"1. Why is faith contrasted with works?\n2. {duplicate}",
                f"1. {duplicate}",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)
            self.assertIn("Duplicate or near-duplicate question", findings[0][1])

    def test_cli_strict_exit_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "1. What does Paul say about faith?\n2. What do [Romans 4:16](https://biblehub.com/bsb/romans/4.htm) and [Ephesians 2:8](https://biblehub.com/bsb/ephesians/2.htm) show about faith?",
                "1. Why is faith contrasted with works?\n2. What stands out to you about living by faith?",
                "1. How should faith shape the way you rely on God?",
            )

            normal = subprocess.run(
                ["python3", str(SCRIPT_PATH), tmpdir],
                capture_output=True,
                text=True,
                check=False,
            )
            strict = subprocess.run(
                ["python3", str(SCRIPT_PATH), "--strict", tmpdir],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(normal.returncode, 0)
            self.assertIn("Question-section findings:", normal.stdout)
            self.assertEqual(strict.returncode, 2)
            self.assertIn("Question-section findings:", strict.stdout)


if __name__ == "__main__":
    unittest.main()
