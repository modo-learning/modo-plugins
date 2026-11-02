"""python3 -m unittest scripts/test_check_rubric_sync.py"""

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_rubric_sync import check  # noqa: E402


def make(tmp, a, b, names=("rubric-v1.1.md", "rubric-v1.1.md")):
    for name, text, file in zip(("assess-my-ai-work", "help-me-improve"), (a, b), names):
        d = pathlib.Path(tmp) / "skills" / name
        d.mkdir(parents=True)
        (d / file).write_text(text)
    return pathlib.Path(tmp)


class RubricSync(unittest.TestCase):
    def test_identical_copies_pass(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(check(make(t, "x", "x")), [])

    def test_diverged_copies_fail(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(len(check(make(t, "x", "y"))), 1)

    def test_copies_of_different_versions_fail(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(check(make(t, "x", "x", ("rubric-v1.1.md", "rubric-v1.md"))))

    def test_missing_copy_fails(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(check(pathlib.Path(t)))

    def test_record_copies_identical_pass(self):
        with tempfile.TemporaryDirectory() as t:
            root = make(t, "x", "x")
            for skill in ("export-assessment", "save-to-passport"):
                d = root / "skills" / skill
                d.mkdir()
                (d / "RECORD.md").write_text("record")
                (d / "assessment-record.schema.json").write_text("{}")
            self.assertEqual(check(root), [])

    def test_record_copy_diverged_fails(self):
        with tempfile.TemporaryDirectory() as t:
            root = make(t, "x", "x")
            for skill, schema in (("export-assessment", "{}"), ("save-to-passport", '{"x": 1}')):
                d = root / "skills" / skill
                d.mkdir()
                (d / "RECORD.md").write_text("record")
                (d / "assessment-record.schema.json").write_text(schema)
            problems = check(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("assessment-record.schema.json", problems[0])

    def test_record_copy_missing_its_schema_fails(self):
        with tempfile.TemporaryDirectory() as t:
            root = make(t, "x", "x")
            for skill in ("export-assessment", "save-to-passport"):
                d = root / "skills" / skill
                d.mkdir()
                (d / "RECORD.md").write_text("record")
            (root / "skills" / "export-assessment" / "assessment-record.schema.json").write_text("{}")
            self.assertEqual(len(check(root)), 1)

    def test_real_plugin_in_sync(self):
        root = pathlib.Path(__file__).parent.parent / "plugins" / "modo-ai-skills"
        self.assertEqual(check(root), [])


if __name__ == "__main__":
    unittest.main()
