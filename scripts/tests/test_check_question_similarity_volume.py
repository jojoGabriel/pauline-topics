import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_question_similarity_volume.py"
SPEC = importlib.util.spec_from_file_location("check_question_similarity_volume", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_module(path: Path, title: str, question: str) -> None:
    path.write_text(
        textwrap.dedent(
            f"""\
---
title: {title}
---

## 9. Observation Questions

1. {question}

## 10. Reflection Questions

1. Why does this matter for {title}?

## 11. Application Questions

1. How should this shape the way you live in {title}?
            """
        ),
        encoding="utf-8",
    )


class CheckQuestionSimilarityVolumeTests(unittest.TestCase):
    def test_repeated_question_across_modules_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            question = "According to [Romans 3:23](https://biblehub.com/bsb/romans/3.htm), what problem do all people share?"
            write_module(Path(tmpdir) / "PT01.md", "Justification", question)
            write_module(Path(tmpdir) / "PT02.md", "Grace", question)
            _, errors, findings = MODULE.analyze_modules(tmpdir)
            self.assertEqual(errors, [])
            self.assertEqual(len(findings), 1)


if __name__ == "__main__":
    unittest.main()
