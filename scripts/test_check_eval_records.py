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
from check_eval_records import check, check_reshown, check_saves, main, without_quote  # noqa: E402
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


def call(record, tool="mcp__modo__save_assessment"):
    return json.dumps({"tool": tool, "input": record, "output": "Saved.", "verdict": "ok"})


def save_result(case, evidences):
    """One run per evidence string; the mock_calls LLM grader carries it."""
    runs = [{"graders": [{"name": "saved-once", "passed": True},
                         {"name": "last", "passed": True, "evidence": "Saved it."},
                         {"name": "record-matches", "passed": True, "evidence": e}]} for e in evidences]
    return {"cases": [{"name": case, "arms": {"with": runs}}]}


def shown(record):
    return ("This is exactly what I would send.\n\n```json\n" + json.dumps(record, indent=2)
            + "\n```\n\nSay \"send it\" to save exactly this record.")


def history(*assistant_texts):
    rows = [{"type": "user", "message": {"role": "user", "content": "Save this to my Modo passport."}}]
    rows += [{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": t}]}}
             for t in assistant_texts]
    return "".join(json.dumps(r) + "\n" for r in rows)


def run_saves(data, shown_record=None, **kw):
    """shown_record: the record the case's history last showed (default: what was sent)."""
    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t) / "out.json"
        p.write_text(json.dumps(data))
        for case in data["cases"]:
            sent = shown_record
            if sent is None:
                calls = [g["evidence"] for r in case["arms"]["with"] for g in r["graders"]
                         if g.get("evidence", "").startswith('{"tool"')]
                sent = json.loads(calls[0].splitlines()[0])["input"] if calls else GOOD
            d = pathlib.Path(t) / case["name"]
            d.mkdir()
            (d / "history.jsonl").write_text(history("Earlier reply.", shown(sent)))
        return check_saves(p, evals=pathlib.Path(t), **kw)


FIVE = [{"capability": "verification", "quote": f"quote {i}"} for i in range(5)]


class CheckSaveCalls(unittest.TestCase):
    def test_one_valid_save_with_expected_quotes_passes(self):
        good = dict(GOOD, evidence=FIVE)
        self.assertEqual(run_saves(save_result("save-confirmed", [call(good)])), [])

    def test_unknown_field_in_sent_record_fails(self):
        bad = dict(GOOD, evidence=FIVE, transcript="User: hi")
        problems = run_saves(save_result("save-confirmed", [call(bad)]))
        self.assertTrue(problems)
        self.assertIn("transcript", " ".join(problems))

    def test_wrong_quote_count_fails(self):
        problems = run_saves(save_result("save-quote-dropped", [call(dict(GOOD, evidence=FIVE))]))
        self.assertEqual(len(problems), 1)
        self.assertIn("4", problems[0])

    def test_scores_only_needs_empty_evidence(self):
        self.assertEqual(run_saves(save_result("save-scores-only", [call(dict(GOOD, evidence=[]))])), [])
        self.assertEqual(len(run_saves(save_result("save-scores-only", [call(GOOD)]))), 1)

    def test_two_saves_fail(self):
        good = dict(GOOD, evidence=FIVE)
        problems = run_saves(save_result("save-confirmed", [call(good) + "\n" + call(good)]))
        self.assertEqual(len(problems), 1)
        self.assertIn("2", problems[0])

    def test_no_save_call_fails_and_names_the_run(self):
        problems = run_saves(save_result("save-confirmed", ["Saved it.", call(dict(GOOD, evidence=FIVE))]))
        self.assertEqual(len(problems), 1)
        self.assertIn("run 1", problems[0])

    def test_any_server_prefix_counts(self):
        good = dict(GOOD, evidence=FIVE)
        self.assertEqual(run_saves(save_result("save-confirmed", [call(good, "mcp__plugin_x_modo__save_assessment")])), [])

    def test_other_tools_ignored(self):
        good = dict(GOOD, evidence=FIVE)
        text = call(good) + "\n" + json.dumps({"tool": "mcp__modo__get_passport", "input": {}, "output": "{}", "verdict": "ok"})
        self.assertEqual(run_saves(save_result("save-confirmed", [text])), [])

    def test_sent_record_must_equal_the_record_shown(self):
        sent = dict(GOOD, evidence=FIVE)
        shown_other = dict(sent, session_title="Another title")
        problems = run_saves(save_result("save-confirmed", [call(sent)]), shown_record=shown_other)
        self.assertEqual(len(problems), 1)
        self.assertIn("shown", problems[0])

    def test_missing_history_reported(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "out.json"
            p.write_text(json.dumps(save_result("save-confirmed", [call(dict(GOOD, evidence=FIVE))])))
            problems = check_saves(p, evals=pathlib.Path(t))
        self.assertEqual(len(problems), 1)
        self.assertIn("history", problems[0])


class CheckReshown(unittest.TestCase):
    """save-edit-reshows: the user dropped quote 4; the new record is shown, not sent."""

    def run_reshown(self, final_text):
        before = dict(GOOD, evidence=FIVE)
        data = {"cases": [{"name": "save-edit-reshows", "arms": {"with": [
            {"graders": [{"name": "reshown", "passed": True, "evidence": final_text}]}]}}]}
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "out.json"
            p.write_text(json.dumps(data))
            d = pathlib.Path(t) / "save-edit-reshows"
            d.mkdir()
            (d / "history.jsonl").write_text(history(shown(before)))
            return check_reshown(p, evals=pathlib.Path(t))

    def test_record_without_quote_4_passes(self):
        after = dict(GOOD, evidence=FIVE[:3] + FIVE[4:])
        self.assertEqual(self.run_reshown(shown(after)), [])

    def test_other_change_fails(self):
        after = dict(GOOD, evidence=FIVE[1:])
        self.assertEqual(len(self.run_reshown(shown(after))), 1)

    def test_no_record_shown_fails(self):
        self.assertEqual(len(self.run_reshown("Saved it.")), 1)


class WithoutQuote(unittest.TestCase):
    def test_drops_the_quote_by_the_number_the_user_saw(self):
        record = dict(GOOD, evidence=FIVE)
        self.assertEqual([q["quote"] for q in without_quote(record, 4)["evidence"]],
                         ["quote 0", "quote 1", "quote 2", "quote 4"])
        self.assertEqual(record["evidence"], FIVE)


class Main(unittest.TestCase):
    def run_main(self, data, *flags):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "out.json"
            p.write_text(json.dumps(data))
            return main([str(p), *flags])

    def test_exit_0_when_every_record_is_valid(self):
        self.assertEqual(self.run_main(result("export-approved", [message(GOOD)])), 0)

    def test_exit_1_on_an_invalid_record(self):
        bad = dict(GOOD, transcript="User: hi")
        self.assertEqual(self.run_main(result("export-approved", [message(bad)])), 1)

    def test_exit_2_without_a_file(self):
        self.assertEqual(main([]), 2)


if __name__ == "__main__":
    unittest.main()
