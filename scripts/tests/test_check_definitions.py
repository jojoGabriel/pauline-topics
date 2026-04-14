import importlib.util
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_definitions.py"
SPEC = importlib.util.spec_from_file_location("check_definitions", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(path: Path, title: str, definition: str, heading: str = "## 1. Definition") -> None:
    path.write_text(
        textwrap.dedent(
            f"""\
            ---
            module_id: PTXX
            title: {title}
            ---

            # {title}

            {heading}

            {definition}

            ---

            ## 2. The Problem / Context

            Placeholder.
            """
        ),
        encoding="utf-8",
    )


class CheckDefinitionsTests(unittest.TestCase):
    def test_self_reference_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir) / "PT03_Faith.md"
            write_module(module_path, "Faith", "Faith refers to faith in God.")

            modules, errors, self_refs, opening_deps, adjacency, cycles = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(len(modules), 1)
            self.assertEqual([item[0].title for item in self_refs], ["Faith"])
            self.assertEqual(opening_deps, [])
            self.assertEqual(adjacency["Faith"], set())
            self.assertEqual(cycles, [])

    def test_acceptable_definition_is_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir) / "PT03_Faith.md"
            write_module(module_path, "Faith", "Trusting God's promise in Christ is the response Paul describes.")

            _, errors, self_refs, opening_deps, adjacency, cycles = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(self_refs, [])
            self.assertEqual(opening_deps, [])
            self.assertEqual(adjacency["Faith"], set())
            self.assertEqual(cycles, [])

    def test_opening_dependency_is_reported_without_cycle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PT07_Reconciliation.md", "Reconciliation", "Restored relationship with God brings peace with God through Christ.")
            write_module(Path(tmpdir) / "PT19_Peace_with_God.md", "Peace with God", "A settled state of peace before God through Jesus Christ.")

            _, errors, self_refs, opening_deps, adjacency, cycles = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(self_refs, [])
            self.assertEqual([item[0].title for item in opening_deps], ["Reconciliation"])
            self.assertEqual(adjacency["Reconciliation"], {"Peace with God"})
            self.assertEqual(adjacency["Peace with God"], set())
            self.assertEqual(cycles, [])

    def test_cycle_between_topics_is_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PTA.md", "Topic A", "Topic B is the meaning of Topic A in this draft.")
            write_module(Path(tmpdir) / "PTB.md", "Topic B", "Topic A is the meaning of Topic B in this draft.")

            _, errors, _, opening_deps, adjacency, cycles = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual([item[0].title for item in opening_deps], ["Topic A", "Topic B"])
            self.assertEqual(adjacency["Topic A"], {"Topic B"})
            self.assertEqual(adjacency["Topic B"], {"Topic A"})
            self.assertEqual(cycles, [["Topic A", "Topic B", "Topic A"]])

    def test_missing_definition_heading_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PT03_Faith.md", "Faith", "Trusting God's promise in Christ.", heading="## 1. Definitions")

            _, errors, self_refs, opening_deps, adjacency, cycles = MODULE.analyze_modules(tmpdir)

            self.assertEqual(len(errors), 1)
            self.assertIn("Missing `## 1. Definition` content", errors[0])
            self.assertEqual(self_refs, [])
            self.assertEqual(opening_deps, [])
            self.assertEqual(adjacency, {})
            self.assertEqual(cycles, [])

    def test_word_boundaries_prevent_false_topic_hits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PT08_Atonement.md", "Atonement", "Christ's sacrificial dealing with human guilt so that sinners may be brought near to God.")
            write_module(Path(tmpdir) / "PT26_Sin.md", "Sin", "Human rebellion against God.")

            _, errors, self_refs, opening_deps, adjacency, cycles = MODULE.analyze_modules(tmpdir)

            self.assertEqual(errors, [])
            self.assertEqual(self_refs, [])
            self.assertEqual(opening_deps, [])
            self.assertEqual(adjacency["Atonement"], set())
            self.assertEqual(cycles, [])

    def test_cli_strict_exit_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PT03_Faith.md", "Faith", "Faith refers to faith in God.")

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
            self.assertIn("Self-referential definitions:", normal.stdout)
            self.assertEqual(strict.returncode, 2)
            self.assertIn("Self-referential definitions:", strict.stdout)


if __name__ == "__main__":
    unittest.main()
