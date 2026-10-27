"""python3 -m unittest scripts/test_check_eval_records.py

The fake result below has the shape of a real aggregate-result.json:
cases[].arms.with[].graders[].evidence holds the final message for LLM graders.
"""

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_eval_records import check  # noqa: E402
from test_validate_assessment_record import GOOD  # noqa: E402


def message(record):
    return "# Report\n\n```json\n" + json.dumps(record, indent=2) + "\n```\n"


def result(case, texts):
    runs = [{"graders": [{"name": "regex", "passed": True},
                         {"name": "llm", "passed": True, "evidence": t}]} for t in texts]
    return {"cases": [{"name": case, "arms": {"with": runs}}]}


def run_check(data, **kw):
    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t) / "out.json"
        p.write_text(json.dumps(data))
        return check(p, **kw)


class CheckEvalRecords(unittest.TestCase):
    def test_valid_runs_pass(self):
        self.assertEqual(run_check(result("export-approved", [message(GOOD)] * 2)), [])

    def test_invalid_record_reported_with_case_and_run(self):
        bad = dict(GOOD, session_title="t" * 121)
        problems = run_check(result("export-approved", [message(GOOD), message(bad)]))
        self.assertEqual(len(problems), 1)
        self.assertIn("export-approved", problems[0])
        self.assertIn("run 2", problems[0])

    def test_missing_block_reported_for_export_cases(self):
        self.assertEqual(len(run_check(result("export-approved", ["no block here"]))), 1)

    def test_no_block_expected_for_other_cases(self):
        self.assertEqual(run_check(result("export-proposes", ["Which quotes do you approve?"])), [])

    def test_scores_only_must_have_empty_evidence(self):
        self.assertEqual(len(run_check(result("export-scores-only", [message(GOOD)]))), 1)
        self.assertEqual(run_check(result("export-scores-only", [message(dict(GOOD, evidence=[]))])), [])

    def test_run_without_final_text_reported(self):
        data = {"cases": [{"name": "export-approved", "arms": {"with": [{"graders": [{"name": "r"}]}]}}]}
        problems = run_check(data)
        self.assertEqual(len(problems), 1)
        self.assertIn("last_message", problems[0])


if __name__ == "__main__":
    unittest.main()
