import importlib.util
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_topic_overlap.py"
SPEC = importlib.util.spec_from_file_location("check_topic_overlap", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(
    path: Path,
    title: str,
    definition: str,
    summary: str,
    key_reference: str = "Romans 1:1",
    illustration_reference: str = "",
) -> None:
    if not illustration_reference:
        illustration_reference = f"Romans {sum(ord(ch) for ch in title) % 50 + 1}:1"
    path.write_text(
        textwrap.dedent(
            f"""\
            ---
            module_id: PTXX
            title: {title}
            ---

            # {title}

            ## 1. Definition

            {definition}

            ---

            ## 2. The Problem / Context

            Placeholder.

            ---

            ## 7. Summary

            {summary}

            ---

            ## 5. Illustration / Example

            <!--
            id: PTXX-Q0
            reference: {illustration_reference}
            source: BSB
            source_url: https://biblehub.com/bsb/romans/2.htm
            type: exact
            ellipsis_allowed: false
            -->

            > "Placeholder"
            >
            > *({illustration_reference})*

            ---

            ## 8. Key Verse

            <!--
            id: PTXX-Q1
            reference: {key_reference}
            source: BSB
            source_url: https://biblehub.com/bsb/romans/1.htm
            type: exact
            ellipsis_allowed: false
            -->

            > "Placeholder"
            >
            > *({key_reference})*
            """
        ),
        encoding="utf-8",
    )


class CheckTopicOverlapTests(unittest.TestCase):
    def test_duplicate_key_verse_is_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT01.md",
                "Justification",
                "God's verdict declaring guilty sinners righteous through Christ.",
                "God declares sinners righteous through Christ.",
                key_reference="Romans 3:28",
            )
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "Trusting God rather than human effort.",
                "Faith receives what God promises.",
                key_reference="Romans 3:28",
            )

            _, errors, duplicate_refs, duplicate_illustrations, similar_defs, similar_summaries = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(duplicate_refs, ["Romans 3:28: Faith, Justification"])
            self.assertEqual(duplicate_illustrations, [])
            self.assertEqual(similar_defs, [])
            self.assertEqual(similar_summaries, [])

    def test_duplicate_illustration_reference_is_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT01.md",
                "Justification",
                "God's verdict declaring guilty sinners righteous through Christ.",
                "God declares sinners righteous through Christ.",
                key_reference="Romans 3:28",
                illustration_reference="Romans 4:3",
            )
            write_module(
                Path(tmpdir) / "PT05.md",
                "Righteousness",
                "The right standing God gives rather than people establish.",
                "God gives right standing through Christ.",
                key_reference="Romans 3:22",
                illustration_reference="Romans 4:3",
            )

            _, errors, duplicate_refs, duplicate_illustrations, similar_defs, similar_summaries = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(duplicate_refs, [])
            self.assertEqual(duplicate_illustrations, ["Romans 4:3: Justification, Righteousness"])
            self.assertEqual(similar_defs, [])
            self.assertEqual(similar_summaries, [])

    def test_similar_definitions_are_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PTA.md",
                "Topic A",
                "God's undeserved favor shown in saving helpless people and sustaining them in Christ.",
                "God saves helpless people and sustains them in Christ.",
            )
            write_module(
                Path(tmpdir) / "PTB.md",
                "Topic B",
                "God's undeserved favor shown in saving helpless people and sustaining them in Christ.",
                "A different summary lives here.",
            )

            _, errors, _, _, similar_defs, _ = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(similar_defs), 1)
            self.assertIn("Topic A <-> Topic B", similar_defs[0])

    def test_similar_summaries_are_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PTA.md",
                "Topic A",
                "Distinct definition one.",
                "God saves helpless people and sustains them in Christ for holy living.",
            )
            write_module(
                Path(tmpdir) / "PTB.md",
                "Topic B",
                "Distinct definition two.",
                "God saves helpless people and sustains them in Christ for holy living.",
            )

            _, errors, _, _, _, similar_summaries = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(similar_summaries), 1)
            self.assertIn("Topic A <-> Topic B", similar_summaries[0])

    def test_clean_modules_are_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PTA.md",
                "Topic A",
                "Trusting God's promise rather than human effort.",
                "Faith receives what God promises and continues in reliance on Him.",
                key_reference="Romans 4:20",
            )
            write_module(
                Path(tmpdir) / "PTB.md",
                "Topic B",
                "God's compassionate action toward helpless people.",
                "Mercy saves the undeserving and leads them to grateful obedience.",
                key_reference="Titus 3:5",
            )

            _, errors, duplicate_refs, duplicate_illustrations, similar_defs, similar_summaries = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(duplicate_refs, [])
            self.assertEqual(duplicate_illustrations, [])
            self.assertEqual(similar_defs, [])
            self.assertEqual(similar_summaries, [])

    def test_cli_strict_exit_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT01.md",
                "Justification",
                "God's verdict declaring guilty sinners righteous through Christ.",
                "God declares sinners righteous through Christ.",
                key_reference="Romans 3:28",
            )
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "Trusting God rather than human effort.",
                "Faith receives what God promises.",
                key_reference="Romans 3:28",
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
            self.assertIn("Duplicate key verse references:", normal.stdout)
            self.assertEqual(strict.returncode, 2)
            self.assertIn("Duplicate key verse references:", strict.stdout)


if __name__ == "__main__":
    unittest.main()
