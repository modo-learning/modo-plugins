"""python3 -m unittest scripts/test_validate_chat_result.py"""

import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate_chat_result import CAPABILITIES, clean_user_message, validate  # noqa: E402

MESSAGES = [
    "Read the RHP and tell me if it is an offer for sale or a fresh issue.",
    "<system-reminder>The user's timezone is Asia/Kolkata. Message sent at Thu</system-reminder>\n"
    "The revenue figure for FY24 looks wrong, check it against page 212.",
    "Now do the same for Adroit Industries.",
    "Give me the report as a PDF, same format as before.",
]


def not_shown():
    return {"level": "not_shown", "confidence": "low", "agreement": "3 of 3 runs", "behaviours": [], "quotes": []}


def good():
    caps = {c: not_shown() for c in CAPABILITIES}
    caps["verification"] = {"level": 3, "confidence": "medium", "agreement": "3 of 3 runs",
                            "behaviours": ["V3b"],
                            "quotes": [{"message": 2, "text": "check it against page 212"}]}
    caps["workflow_design"] = {"level": 4, "confidence": "low", "agreement": "2 of 3 runs",
                               "behaviours": ["W4a"],
                               "quotes": [{"message": 4, "text": "same format as before"}]}
    return {"chat_id": "4d30a8de", "title": "NSE company financial analysis", "updated_at": "2026-10-30T12:01:00Z",
            "turns_total": 9, "user_messages": 4, "unreadable_turns": 1, "attachments_seen": True,
            "truncated_turns": [], "too_short": False, "runs": 3, "run_kind": "subagents", "capabilities": caps}


def too_short():
    r = good()
    r.update(user_messages=3, too_short=True, runs=0, run_kind="none")
    for c in CAPABILITIES:
        r["capabilities"][c] = dict(not_shown(), agreement="")
    return r


class Valid(unittest.TestCase):
    def test_a_good_result_passes_with_and_without_messages(self):
        self.assertEqual(validate(good()), [])
        self.assertEqual(validate(good(), MESSAGES), [])

    def test_a_too_short_result_passes(self):
        self.assertEqual(validate(too_short()), [])

    def test_five_runs_and_disagreement(self):
        r = good()
        r["runs"] = 5
        r["capabilities"]["verification"]["agreement"] = "4 of 5 runs"
        r["capabilities"]["workflow_design"] = dict(not_shown(), agreement="runs disagreed")
        for c in ("problem_solving", "delegation", "strategic_thinking"):
            r["capabilities"][c]["agreement"] = "5 of 5 runs"
        self.assertEqual(validate(r), [])


class Invalid(unittest.TestCase):
    def check(self, mutate, expected, messages=None):
        r = good()
        mutate(r)
        errors = validate(r, messages)
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_paraphrased_quote(self):
        self.check(lambda r: r["capabilities"]["verification"]["quotes"][0].update(text="check it on page 212"),
                   "not a word-for-word excerpt of user message 2", MESSAGES)

    def test_quote_from_the_wrong_message(self):
        self.check(lambda r: r["capabilities"]["verification"]["quotes"][0].update(message=1),
                   "not a word-for-word excerpt of user message 1", MESSAGES)

    def test_quote_from_the_reminder_is_not_the_user(self):
        self.check(lambda r: r["capabilities"]["verification"]["quotes"][0].update(text="Asia/Kolkata"),
                   "not a word-for-word excerpt", MESSAGES)

    def test_quote_number_beyond_user_messages(self):
        self.check(lambda r: r["capabilities"]["verification"]["quotes"][0].update(message=9),
                   "must be a user message number")

    def test_long_quote(self):
        self.check(lambda r: r["capabilities"]["verification"]["quotes"][0].update(text="a" * 241), "1 to 240")

    def test_level_without_quote(self):
        self.check(lambda r: r["capabilities"]["verification"].update(quotes=[]), "needs at least one quote")

    def test_not_shown_with_evidence(self):
        self.check(lambda r: r["capabilities"]["delegation"].update(behaviours=["D3a"]), "has no behaviours or quotes")

    def test_behaviour_of_another_capability(self):
        self.check(lambda r: r["capabilities"]["verification"].update(behaviours=["D3a"]), "not a rubric v1.1 verification")

    def test_unknown_behaviour(self):
        self.check(lambda r: r["capabilities"]["verification"].update(behaviours=["V9z"]), "not a rubric v1.1")

    def test_level_out_of_range(self):
        self.check(lambda r: r["capabilities"]["verification"].update(level=6), "1 to 5")

    def test_agreement_runs_mismatch(self):
        self.check(lambda r: r["capabilities"]["verification"].update(agreement="4 of 5 runs"), "says 5 runs but runs is 3")

    def test_disagreed_must_be_not_shown(self):
        self.check(lambda r: r["capabilities"]["verification"].update(agreement="runs disagreed"), "when the runs disagreed")

    def test_unknown_and_missing_fields(self):
        self.check(lambda r: r.update(transcript="the whole chat"), "unknown field(s) ['transcript']")
        self.check(lambda r: r.pop("chat_id"), "missing field(s) ['chat_id']")

    def test_capabilities_out_of_order(self):
        def swap(r):
            caps = r["capabilities"]
            r["capabilities"] = {k: caps[k] for k in reversed(CAPABILITIES)}
        self.check(swap, "in that order")

    def test_too_short_flag_must_match_count(self):
        self.check(lambda r: r.update(user_messages=3), "too_short: must be true exactly")

    def test_too_short_must_not_score(self):
        r = too_short()
        r["capabilities"]["verification"] = copy.deepcopy(good()["capabilities"]["verification"])
        self.assertTrue(any('must be "not_shown" for a chat that is too short' in e for e in validate(r)))

    def test_runs_and_kind(self):
        self.check(lambda r: r.update(runs=4), "runs: must be 3 or 5")
        self.check(lambda r: r.update(run_kind="none"), '"none" only for a chat that is too short')

    def test_bool_is_not_a_count(self):
        self.check(lambda r: r.update(turns_total=True), "turns_total: must be an integer")


class Clean(unittest.TestCase):
    def test_strips_only_the_leading_reminder(self):
        self.assertEqual(clean_user_message(MESSAGES[1]),
                         "The revenue figure for FY24 looks wrong, check it against page 212.")
        self.assertEqual(clean_user_message("no reminder here"), "no reminder here")
        self.assertEqual(clean_user_message("text <system-reminder>x</system-reminder>"),
                         "text <system-reminder>x</system-reminder>")


if __name__ == "__main__":
    unittest.main()
