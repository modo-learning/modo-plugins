"""python3 -m unittest scripts/test_run_save_evals.py

The eval runner is replaced by a fake that writes an aggregate-result.json
where the real one would; the record checks run for real against the
committed save-confirmed history."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_eval_records import EVALS, shown_record  # noqa: E402
from run_save_evals import main  # noqa: E402

SHOWN = shown_record(EVALS / "save-confirmed")


def result(record):
    call = json.dumps({"tool": "mcp__modo__save_assessment", "input": record, "output": "Saved.", "verdict": "ok"})
    return {"cases": [{"name": "save-confirmed", "arms": {"with": [
        {"graders": [{"name": "record-matches", "passed": True, "evidence": call}]}]}}]}


class FakeEval:
    """Stands in for `claude plugin eval`: writes `data` and exits with `code`."""

    def __init__(self, data, code=0):
        self.data, self.code, self.commands = data, code, []

    def __call__(self, cmd, **_):
        self.commands.append(cmd)
        if self.data is not None:
            out = pathlib.Path(cmd[cmd.index("--output-dir") + 1])
            out.mkdir(parents=True, exist_ok=True)
            (out / "aggregate-result.json").write_text(json.dumps(self.data))
        return subprocess.CompletedProcess(cmd, self.code)


def run(fake, *args):
    with tempfile.TemporaryDirectory() as t:
        return main(["--output-dir", t, *args, "save-confirmed"], run=fake)


class RunSaveEvals(unittest.TestCase):
    def test_passes_when_the_eval_and_the_record_check_pass(self):
        self.assertEqual(run(FakeEval(result(SHOWN))), 0)

    def test_fails_on_an_unknown_field_although_the_eval_passed(self):
        self.assertEqual(run(FakeEval(result(dict(SHOWN, transcript="User: hi")))), 1)

    def test_fails_on_more_than_five_quotes_although_the_eval_passed(self):
        six = SHOWN["evidence"] + SHOWN["evidence"][:1]
        self.assertEqual(run(FakeEval(result(dict(SHOWN, evidence=six)))), 1)

    def test_fails_when_nothing_was_sent_although_the_eval_passed(self):
        self.assertEqual(run(FakeEval({"cases": [{"name": "save-confirmed", "arms": {"with": [{"graders": []}]}}]})), 1)

    def test_fails_when_the_eval_fails(self):
        self.assertEqual(run(FakeEval(result(SHOWN), code=1)), 1)

    def test_fails_without_a_result_file(self):
        self.assertEqual(run(FakeEval(None)), 1)

    def test_runs_the_named_case_with_the_given_runs(self):
        fake = FakeEval(result(SHOWN))
        run(fake, "--runs", "2")
        cmd = fake.commands[0]
        self.assertEqual(cmd[:3], ["claude", "plugin", "eval"])
        self.assertEqual(cmd[cmd.index("--case") + 1], "save-confirmed")
        self.assertEqual(cmd[cmd.index("--runs") + 1], "2")


if __name__ == "__main__":
    unittest.main()
