import importlib.util
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_summaries.py"
SPEC = importlib.util.spec_from_file_location("check_summaries", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(path: Path, title: str, definition: str, summary: str, summary_heading: str = "## 7. Summary") -> None:
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

            {summary_heading}

            {summary}

            ---

            ## 8. Key Verse

            <!--
            id: PTXX-Q1
            reference: Romans 1:1
            source: BSB
            source_url: https://biblehub.com/bsb/romans/1.htm
            type: exact
            ellipsis_allowed: false
            -->

            > "Placeholder"
            >
            > *(Romans 1:1)*
            """
        ),
        encoding="utf-8",
    )


class CheckSummariesTests(unittest.TestCase):
    def test_summary_opening_dependency_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT07.md",
                "Reconciliation",
                "The restoration of a broken relationship with God through Christ.",
                "Peace with God is now the believer's standing before Him. Reconciliation restores fellowship.",
            )
            write_module(
                Path(tmpdir) / "PT19.md",
                "Peace with God",
                "The settled end of hostility before God through Christ.",
                "Believers now have peace with God through Christ.",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 2)
            self.assertIn("Summary opening leans on adjacent topic title(s)", findings[0][1])
            self.assertIn("Summary introduces neighboring topic title(s)", findings[1][1])

    def test_summary_mentions_new_neighbor_topic_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT08.md",
                "Atonement",
                "Christ's sacrificial dealing with human guilt.",
                "Christ is the sacrifice for guilt. This leads to peace with God.",
            )
            write_module(
                Path(tmpdir) / "PT19.md",
                "Peace with God",
                "The settled end of hostility before God through Christ.",
                "Believers now have peace with God through Christ.",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)
            self.assertIn("Summary introduces neighboring topic title(s)", findings[0][1])

    def test_aligned_summary_is_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "Trusting God's promise in Christ rather than human effort.",
                "Faith receives what God promises and continues as the way believers live.",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(findings, [])

    def test_missing_summary_heading_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT03.md",
                "Faith",
                "Trusting God's promise in Christ rather than human effort.",
                "Faith receives what God promises and continues as the way believers live.",
                summary_heading="## 7. Summaries",
            )

            _, errors, findings = MODULE.analyze_modules(tmpdir)

            self.assertEqual(len(errors), 1)
            self.assertIn("Missing `## 7. Summary` content", errors[0])
            self.assertEqual(findings, [])

    def test_cli_strict_exit_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(
                Path(tmpdir) / "PT07.md",
                "Reconciliation",
                "The restoration of a broken relationship with God through Christ.",
                "Peace with God is now the believer's standing before Him. Reconciliation restores fellowship.",
            )
            write_module(
                Path(tmpdir) / "PT19.md",
                "Peace with God",
                "The settled end of hostility before God through Christ.",
                "Believers now have peace with God through Christ.",
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
            self.assertIn("Summary alignment findings:", normal.stdout)
            self.assertEqual(strict.returncode, 2)
            self.assertIn("Summary alignment findings:", strict.stdout)


if __name__ == "__main__":
    unittest.main()
