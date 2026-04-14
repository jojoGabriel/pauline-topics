import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_broader_connections.py"
SPEC = importlib.util.spec_from_file_location("check_broader_connections", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(path: Path, title: str, connections: str = "") -> None:
    extra = ""
    if connections:
        extra = f"\n## 12. Broader Scripture Connections (Optional)\n\n{connections}\n"
    path.write_text(
        textwrap.dedent(
            f"""\
---
title: {title}
---
{extra}
            """
        ),
        encoding="utf-8",
    )


class CheckBroaderConnectionsTests(unittest.TestCase):
    def test_reference_only_lines_are_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PT01.md", "Justification", "- Romans 3:28\n- [James 2:24](https://example.com)")
            _, errors, findings = MODULE.analyze_modules(tmpdir)
            self.assertEqual(errors, [])
            self.assertEqual(findings, [])

    def test_explanatory_line_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_module(Path(tmpdir) / "PT01.md", "Justification", "- Romans 3:28 because this explains it.")
            _, errors, findings = MODULE.analyze_modules(tmpdir)
            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)


if __name__ == "__main__":
    unittest.main()
