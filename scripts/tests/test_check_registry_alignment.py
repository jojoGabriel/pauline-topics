import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_registry_alignment.py"
SPEC = importlib.util.spec_from_file_location("check_registry_alignment", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_registry(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            - [ ] PT-01 Justification by Faith
            - [ ] PT-02 Grace
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


class CheckRegistryAlignmentTests(unittest.TestCase):
    def test_clean_alignment_is_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            modules_dir = tmp / "modules"
            modules_dir.mkdir()
            write_registry(tmp / "topics.md")
            write_module(modules_dir / "PT02_Grace.md", "PT02", "Grace")

            _, errors, findings = MODULE.analyze_modules(str(modules_dir), str(tmp / "topics.md"))
            self.assertEqual(errors, [])
            self.assertEqual(findings, [])

    def test_title_and_filename_mismatch_are_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            modules_dir = tmp / "modules"
            modules_dir.mkdir()
            write_registry(tmp / "topics.md")
            write_module(modules_dir / "PT02_Gift.md", "PT02", "Gift")

            _, errors, findings = MODULE.analyze_modules(str(modules_dir), str(tmp / "topics.md"))
            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 2)


if __name__ == "__main__":
    unittest.main()
