"""python3 -m unittest scripts/test_check_rubric_sync.py"""

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_rubric_sync import check  # noqa: E402


def make(tmp, a, b):
    for name, text in (("assess-my-ai-work", a), ("help-me-improve", b)):
        d = pathlib.Path(tmp) / "skills" / name
        d.mkdir(parents=True)
        (d / "rubric-v1.md").write_text(text)
    return pathlib.Path(tmp)


class RubricSync(unittest.TestCase):
    def test_identical_copies_pass(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(check(make(t, "x", "x")), [])

    def test_diverged_copies_fail(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(len(check(make(t, "x", "y"))), 1)

    def test_missing_copy_fails(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(check(pathlib.Path(t)))

    def test_real_plugin_in_sync(self):
        root = pathlib.Path(__file__).parent.parent / "plugins" / "modo-ai-skills"
        self.assertEqual(check(root), [])


if __name__ == "__main__":
    unittest.main()
