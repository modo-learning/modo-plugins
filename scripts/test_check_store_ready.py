"""python3 -m unittest scripts/test_check_store_ready.py

Covers the repo-specific checks only (rubric copies, raw eval run files);
`claude plugin validate` is skipped here (run_validate=False).
"""

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_store_ready import check  # noqa: E402

README = "A plugin README. " * 20


def plugin(tmp, rubrics=()):
    root = pathlib.Path(tmp) / "demo"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(
        {"name": "demo", "description": "d", "author": {"name": "a"}, "version": "0.1.0"}))
    (root / "LICENSE").write_text("MIT")
    (root / "README.md").write_text(README)
    for skill, text in rubrics:
        d = root / "skills" / skill
        d.mkdir(parents=True)
        (d / "rubric-v1.md").write_text(text)
    return root


def rubric_problems(problems):
    return [p for p in problems if "rubric" in p]


class StoreReady(unittest.TestCase):
    def test_diverged_rubric_copies_block(self):
        with tempfile.TemporaryDirectory() as t:
            problems, _, _ = check(plugin(t, [("a", "x"), ("b", "y")]), run_validate=False)
            self.assertEqual(len(rubric_problems(problems)), 1)

    def test_identical_rubric_copies_pass(self):
        with tempfile.TemporaryDirectory() as t:
            problems, _, _ = check(plugin(t, [("a", "x"), ("b", "x")]), run_validate=False)
            self.assertEqual(problems, [])

    def test_single_rubric_is_not_a_sync_problem(self):
        with tempfile.TemporaryDirectory() as t:
            problems, _, _ = check(plugin(t, [("a", "x")]), run_validate=False)
            self.assertEqual(problems, [])

    def test_no_rubric_at_all_passes(self):
        with tempfile.TemporaryDirectory() as t:
            problems, _, _ = check(plugin(t), run_validate=False)
            self.assertEqual(problems, [])

    def test_raw_eval_run_files_are_mentioned_with_the_clean_script(self):
        with tempfile.TemporaryDirectory() as t:
            root = plugin(t)
            case = root / "evals" / "case"
            case.mkdir(parents=True)
            (case / "0b7c5a52-3f6e-4d1a-9c2b-5e8f1a2b3c4d.jsonl").write_text("{}\n")
            problems, holds, _ = check(root, run_validate=False)
            self.assertEqual(problems, [])
            self.assertTrue(any("clean_eval_runs.py" in h for h in holds), holds)

    def test_no_clean_mention_without_raw_run_files(self):
        with tempfile.TemporaryDirectory() as t:
            _, holds, _ = check(plugin(t), run_validate=False)
            self.assertFalse(any("clean_eval_runs.py" in h for h in holds), holds)


if __name__ == "__main__":
    unittest.main()
