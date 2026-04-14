import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_volume_coverage.py"
SPEC = importlib.util.spec_from_file_location("check_volume_coverage", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_volume(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            - [ ] V1-01 / PT-01 — Justification by Faith
            - [ ] V1-02 / PT-02 — Grace
            """
        ),
        encoding="utf-8",
    )


def write_module(path: Path, module_id: str, title: str) -> None:
    path.write_text(
        textwrap.dedent(
            f"""\
            ---
            module_id: {module_id}
            title: {title}
            ---
            """
        ),
        encoding="utf-8",
    )


class CheckVolumeCoverageTests(unittest.TestCase):
    def test_missing_planned_topic_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            modules_dir = tmp / "modules"
            modules_dir.mkdir()
            write_volume(tmp / "Volume1_Topics_FINAL.md")
            write_module(modules_dir / "PT01_Justification_by_Faith.md", "PT01", "Justification by Faith")

            _, errors, findings = MODULE.analyze_modules(str(modules_dir), str(tmp / "Volume1_Topics_FINAL.md"))
            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)
            self.assertIn("Missing planned volume topics", findings[0])

    def test_unexpected_module_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            modules_dir = tmp / "modules"
            modules_dir.mkdir()
            write_volume(tmp / "Volume1_Topics_FINAL.md")
            write_module(modules_dir / "PT01_Justification_by_Faith.md", "PT01", "Justification by Faith")
            write_module(modules_dir / "PT99_Extra.md", "PT99", "Extra")

            _, errors, findings = MODULE.analyze_modules(str(modules_dir), str(tmp / "Volume1_Topics_FINAL.md"))
            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 2)


if __name__ == "__main__":
    unittest.main()
