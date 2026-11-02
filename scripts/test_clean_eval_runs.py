"""python3 -m unittest scripts/test_clean_eval_runs.py"""

import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from clean_eval_runs import main, raw_runs  # noqa: E402

RUN_ID = "0b7c5a52-3f6e-4d1a-9c2b-5e8f1a2b3c4d"


def plant(repo):
    """A repo with one raw run file and one raw run folder, plus files to keep."""
    case = repo / "plugins" / "demo" / "evals" / "some-case"
    (case / "resources").mkdir(parents=True)
    (case / "history.jsonl").write_text("{}\n")
    (case / "resources" / "session.jsonl").write_text("{}\n")
    (case / f"{RUN_ID}.jsonl").write_text("{}\n")
    (case / RUN_ID / "subagents").mkdir(parents=True)
    (case / RUN_ID / "subagents" / "a.jsonl").write_text("{}\n")
    return case


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(list(argv))
    return code, out.getvalue()


class CleanRuns(unittest.TestCase):
    def test_finds_only_run_files_and_folders(self):
        with tempfile.TemporaryDirectory() as t:
            case = plant(pathlib.Path(t))
            found = raw_runs(pathlib.Path(t) / "plugins" / "demo")
            self.assertEqual(sorted(found), sorted([case / f"{RUN_ID}.jsonl", case / RUN_ID]))

    def test_dry_run_by_default_deletes_nothing(self):
        with tempfile.TemporaryDirectory() as t:
            case = plant(pathlib.Path(t))
            code, out = run(t)
            self.assertEqual(code, 0)
            self.assertIn(RUN_ID, out)
            self.assertTrue((case / f"{RUN_ID}.jsonl").exists())
            self.assertTrue((case / RUN_ID).is_dir())

    def test_delete_removes_runs_and_keeps_everything_else(self):
        with tempfile.TemporaryDirectory() as t:
            case = plant(pathlib.Path(t))
            code, _ = run(t, "--delete")
            self.assertEqual(code, 0)
            self.assertFalse((case / f"{RUN_ID}.jsonl").exists())
            self.assertFalse((case / RUN_ID).exists())
            self.assertTrue((case / "history.jsonl").exists())
            self.assertTrue((case / "resources" / "session.jsonl").exists())

    def test_name_that_only_looks_like_a_uuid_is_kept(self):
        with tempfile.TemporaryDirectory() as t:
            case = plant(pathlib.Path(t))
            (case / "a-b-c-d-e.jsonl").write_text("{}\n")
            self.assertNotIn(case / "a-b-c-d-e.jsonl", raw_runs(pathlib.Path(t) / "plugins" / "demo"))


if __name__ == "__main__":
    unittest.main()
