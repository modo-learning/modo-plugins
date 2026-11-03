"""python3 -m unittest scripts/test_derive_levels.py

The expected values come from rubric v1.1 itself: its worked examples table
and its behaviour tables are parsed and replayed against the reference
implementation, so the published rule and the code cannot drift apart. The
run-combining and coverage cases are written out by hand from the rubric's
"Running it more than once" and "Coverage" sections.
"""

import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import subprocess  # noqa: E402
import json  # noqa: E402
from derive_levels import BEHAVIOURS, RunsError, assess, combine, coverage, derive, overall, self_check  # noqa: E402

RUBRIC = (pathlib.Path(__file__).resolve().parent.parent / "plugins" / "modo-ai-skills"
          / "skills" / "assess-my-ai-work" / "rubric-v1.1.md")


def worked_examples():
    text = RUBRIC.read_text(encoding="utf-8")
    section = text.split("### Worked examples", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or not cells[1].isdigit():
            continue
        seen = []
        if cells[0] != "none":
            for part in cells[0].split(";"):
                msg, ids = part.split(":")
                seen += [(int(msg), i.strip()) for i in ids.split(",")]
        level = cells[2] if cells[2] == "not shown" else int(cells[2])
        rows.append((line, seen, int(cells[1]), level, cells[3] or None))
    return rows


def rubric_behaviours():
    text = RUBRIC.read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"^\| ([PVWDS][1-5][a-z]?) \| ([1-5]) \|", text, re.M)}


class Derive(unittest.TestCase):
    def test_every_worked_example_in_the_rubric(self):
        rows = worked_examples()
        self.assertGreaterEqual(len(rows), 10)
        for line, seen, messages, level, confidence in rows:
            with self.subTest(line):
                self.assertEqual(derive(seen, messages), (level, confidence))

    def test_behaviour_table_matches_the_rubric(self):
        self.assertEqual(BEHAVIOURS, rubric_behaviours())


class Combine(unittest.TestCase):
    def test_unanimous_keeps_the_rule_confidence(self):
        self.assertEqual(combine([(4, "high")] * 3),
                         {"level": 4, "confidence": "high", "agreement": "3 of 3 runs"})

    def test_spread_one_caps_at_medium_and_takes_the_median(self):
        self.assertEqual(combine([(4, "high"), (3, "high"), (4, "high")]),
                         {"level": 4, "confidence": "medium", "agreement": "2 of 3 runs"})

    def test_even_count_takes_the_lower_middle(self):
        runs = [(3, "medium"), (4, "medium"), (4, "medium"), (3, "medium"), ("not shown", None)]
        self.assertEqual(combine(runs),
                         {"level": 3, "confidence": "low", "agreement": "2 of 5 runs"})

    def test_spread_two_is_low(self):
        self.assertEqual(combine([(2, "medium"), (3, "medium"), (4, "high")])["confidence"], "low")

    def test_spread_three_abstains(self):
        self.assertEqual(combine([(1, "low"), (4, "medium"), (4, "medium"), (2, "low"), (3, "low")]),
                         {"level": "runs disagreed", "confidence": None, "agreement": "runs disagreed"})

    def test_majority_not_shown(self):
        self.assertEqual(combine([("not shown", None), ("not shown", None), (2, "low")]),
                         {"level": "not shown", "confidence": None, "agreement": "2 of 3 runs"})

    def test_lowest_confidence_of_the_runs_with_the_final_level(self):
        self.assertEqual(combine([(3, "high"), (3, "low"), (3, "medium")])["confidence"], "low")


class Coverage(unittest.TestCase):
    NAMES = ("Problem Solving", "Verification", "Workflow Design", "Delegation", "Strategic Thinking")

    def levels(self, *values):
        return dict(zip(self.NAMES, values))

    def test_all_five_says_nothing(self):
        self.assertIsNone(coverage(self.levels(3, 4, 2, 2, 3)))

    def test_four_names_the_missing_one(self):
        self.assertEqual(coverage(self.levels(3, 4, 2, 2, "not shown")),
                         "This chat shows 4 of 5 capabilities. One more chat with different "
                         "work could show Strategic Thinking.")

    def test_runs_disagreed_counts_as_shown(self):
        self.assertIsNone(coverage(self.levels(3, 4, 2, "runs disagreed", 3)))

    def test_three_or_fewer_is_partial(self):
        self.assertEqual(coverage(self.levels(3, "not shown", 2, "not shown", "not shown")),
                         "This chat shows only 2 of 5 capabilities, so this is a partial picture. "
                         "Assess 2–3 more chats with different kinds of work to see the rest.")


# The pasted eval chat (strong-verify-weak-delegate) as one run notes it: the
# user re-checks numbers (V), hands the recommendations over vaguely and the
# whole deck at the end without checking it (D1u in message 7).
RUN = {
    "Verification": [[2, "V4b"], [3, "V4a"], [5, "V4a"], [6, "V5a"], [7, "V4c"]],
    "Problem Solving": [[1, "P3a"], [6, "P4a"], [6, "P4b"]],
    "Workflow Design": [[6, "W2a"]],
    "Delegation": [[4, "D1"], [6, "D4a"], [7, "D1u"]],
    "Strategic Thinking": [[1, "S2a"]],
}


class Assess(unittest.TestCase):
    def test_an_unchecked_handoff_caps_delegation_at_3_even_with_a_tier_4_moment(self):
        out = assess({"user_messages": 7, "runs": [RUN, RUN, RUN]})
        d = out["capabilities"]["Delegation"]
        self.assertLessEqual(d["level"], 3)
        self.assertEqual(out["capabilities"]["Verification"]["level"], 5)
        self.assertFalse(out["needs_more_runs"])

    def test_three_runs_that_differ_ask_for_two_more(self):
        other = dict(RUN, **{"Workflow Design": [[6, "W3b"]]})
        out = assess({"user_messages": 7, "runs": [RUN, RUN, other]})
        self.assertTrue(out["needs_more_runs"])
        self.assertEqual(out["capabilities"]["Workflow Design"]["runs"], [2, 2, 3])
        five = assess({"user_messages": 7, "runs": [RUN, RUN, other, RUN, RUN]})
        self.assertFalse(five["needs_more_runs"])
        self.assertEqual(five["capabilities"]["Workflow Design"]["level"], 2)
        self.assertEqual(five["capabilities"]["Workflow Design"]["agreement"], "4 of 5 runs")

    def test_a_capability_left_out_is_not_shown_and_coverage_says_so(self):
        run = {k: v for k, v in RUN.items() if k != "Strategic Thinking"}
        out = assess({"user_messages": 7, "runs": [run, run, run]})
        self.assertEqual(out["capabilities"]["Strategic Thinking"]["level"], "not shown")
        self.assertIn("Strategic Thinking", out["coverage"])

    def test_bad_input_is_rejected(self):
        for data, msg in [
            ({"user_messages": 7, "runs": [RUN, RUN]}, "3 or 5"),
            ({"user_messages": 7, "runs": [dict(RUN, Verification=[[2, "D3a"]])] * 3}, "not a Verification"),
            ({"user_messages": 7, "runs": [dict(RUN, Verification=[[9, "V3b"]])] * 3}, "not 1 to 7"),
            ({"user_messages": 7, "runs": [dict(RUN, Creativity=[])] * 3}, "capability names"),
            ({"runs": [RUN] * 3}, "with optional"),
        ]:
            with self.subTest(msg=msg), self.assertRaisesRegex(RunsError, msg):
                assess(data)

    def test_command_line_prints_json_and_fails_cleanly(self):
        script = pathlib.Path(__file__).parent / "derive_levels.py"
        ok = subprocess.run([sys.executable, "-I", str(script)], input=json.dumps(
            {"user_messages": 7, "runs": [RUN] * 3}), capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertLessEqual(json.loads(ok.stdout)["capabilities"]["Delegation"]["level"], 3)
        self.assertIn(json.loads(ok.stdout)["overall"]["title"], ("Explorer", "Practitioner", "Delegator", "Orchestrator"))
        bad = subprocess.run([sys.executable, "-I", str(script)], input="{}", capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("error:", bad.stderr)


MESSAGES = [
    "Write up my Q3 pricing analysis for the board.",
    "Before I use any of this I recomputed the tier growth myself. Team is 310 against 280.",
    "What is that based on? Give me a source I can open.",
    "Now just write the recommendations section, whatever you think is best.",
    "Where does the $45k come from? Walk me through the arithmetic.",
    "Rerun it three ways. I'll check the three results against my own spreadsheet before they go in the deck.",
    "The third is off by $2k, so fix that one. Then finish the rest of the deck, all the slides.",
]
Q = {"V": [2, "V4b", "I recomputed the tier growth myself"],
     "D4a": [6, "D4a", "Rerun it three ways."],
     "D1u": [7, "D1u", "finish the rest of the deck, all the slides"]}


class Honesty(unittest.TestCase):
    def test_identical_runs_count_once_and_the_runs_line_says_so(self):
        out = assess({"user_messages": 7, "runs": [RUN, RUN, RUN]})
        self.assertEqual(out["runs_used"], 1)
        self.assertTrue(out["runs_line"].startswith("Scored once"))
        self.assertEqual(out["capabilities"]["Verification"]["agreement"], "1 of 1 runs")
        self.assertFalse(out["needs_more_runs"])

    def test_different_runs_report_real_agreement(self):
        other = dict(RUN, **{"Workflow Design": [[6, "W3b"]]})
        out = assess({"user_messages": 7, "runs": [RUN, other, RUN], "run_kind": "subagents"})
        self.assertEqual(out["runs_used"], 3)
        self.assertEqual(out["runs_line"], "Scored 3 times (as separate sub-tasks); the runs agreed on 4 of 5 capabilities.")
        self.assertTrue(out["needs_more_runs"])

    def test_with_messages_a_behaviour_needs_the_users_exact_words(self):
        run = {"Verification": [Q["V"]], "Delegation": [Q["D4a"], Q["D1u"],
                                                     [5, "D4b", "words the user never wrote"]]}
        other = {"Verification": [Q["V"]], "Delegation": [Q["D4a"], Q["D1u"]], "Strategic Thinking": [[1, "S2a", "for the board"]]}
        out = assess({"user_messages": 7, "messages": MESSAGES, "runs": [run, other, run]})
        self.assertEqual(out["dropped"], ["run 1, Delegation: D4b in message 5 (no exact quote from that message)",
                                          "run 3, Delegation: D4b in message 5 (no exact quote from that message)"])
        self.assertLessEqual(out["capabilities"]["Delegation"]["level"], 3)

    def test_a_quote_from_another_message_is_dropped(self):
        wrong = [3, "V4b", "I recomputed the tier growth myself"]
        out = assess({"user_messages": 7, "messages": MESSAGES, "runs": [{"Verification": [wrong]}] * 3})
        self.assertEqual(len(out["dropped"]), 3)
        self.assertEqual(out["capabilities"]["Verification"]["level"], "not shown")

    def test_messages_must_match_the_count(self):
        with self.assertRaisesRegex(RunsError, "messages must be"):
            assess({"user_messages": 7, "messages": MESSAGES[:3], "runs": [RUN] * 3})

    def test_self_check_passes_and_is_reported(self):
        self.assertEqual(self_check(), "passed")
        out = assess({"user_messages": 7, "runs": [RUN] * 3})
        self.assertEqual((out["self_check"], out["script_version"]), ("passed", "rubric-v1.1-levels-3"))


# The overall AI fluency level (Modo's ladder, "AI Fluency Levels", Johnny,
# 2026-11-02): the highest L in 1..4 that at least 3 of the 5 capabilities
# reach; fewer than 3 with a level gives none; Level 5 is never given from
# chats. Decided 2026-11-03, flag for review (Angelina, Johnny).
# Five capability levels in rubric order -> (overall level, title).
OVERALL_WORKED = [
    ([4, 4, 3, 2, "not_shown"], (3, "Delegator")),
    ([5, 5, 5, 5, 5], (4, "Orchestrator")),
    ([2, "not_shown", "not_shown", "not_shown", 1], (None, None)),
    ([3, 3, 2, 2, 2], (2, "Practitioner")),
    ([1, 1, 1, 1, 1], (1, "Explorer")),
    ([1, 1, 1, "not shown", "not shown"], (1, "Explorer")),
    ([5, 5, 5, 1, 1], (4, "Orchestrator")),
    ([5, 4, 1, 1, "not_shown"], (1, "Explorer")),
    ([4, 4, "runs disagreed", 4, "not shown"], (4, "Orchestrator")),
    ([4, 4, "runs disagreed", "not shown", "not shown"], (None, None)),
    (["not_shown"] * 5, (None, None)),
]


class Overall(unittest.TestCase):
    def test_the_worked_examples_table(self):
        for levels, want in OVERALL_WORKED:
            with self.subTest(levels=levels):
                got = overall(levels)
                self.assertEqual((got["level"], got["title"]), want)

    def test_the_line_names_the_title_and_the_rule(self):
        self.assertEqual(overall([4, 4, 3, 2, "not_shown"])["line"],
                         "Overall: Delegator (Level 3 of 4 on Modo's AI fluency ladder from chats; "
                         "at least 3 of your 5 capabilities are at Level 3 or higher).")

    def test_not_enough_shown_says_how_many_have_a_level(self):
        self.assertEqual(overall([2, "not_shown", "not_shown", "not_shown", 1])["line"],
                         "Overall: not enough shown (only 2 of your 5 capabilities have a level; "
                         "an overall level needs at least 3).")
        self.assertEqual(overall([2] + ["not shown"] * 4)["line"],
                         "Overall: not enough shown (only 1 of your 5 capabilities has a level; "
                         "an overall level needs at least 3).")

    def test_the_multiplier_note_only_at_the_top_level_from_chats(self):
        note = overall([5, 5, 5, 5, 5])["note"]
        self.assertEqual(note, "Level 5 (Multiplier) is never given from chats: it needs evidence a chat "
                               "doesn't hold, such as assets or agents your colleagues adopt and tracked time saved.")
        self.assertIsNone(overall([4, 4, 3, 2, "not_shown"])["note"])
        self.assertIsNone(overall(["not_shown"] * 5)["note"])

    def test_accepts_a_mapping_of_capability_levels(self):
        levels = dict(zip(Coverage.NAMES, [4, 4, 3, 2, "not shown"]))
        self.assertEqual(overall(levels)["level"], 3)

    def test_both_assess_skills_state_the_same_lines_and_rule(self):
        skills = RUBRIC.parent.parent
        lines = [overall([4, 4, 3, 2, "not_shown"])["line"], overall([5, 5, 5, 5, 5])["note"]]
        generic = (overall([4, 4, 3, 2, "not_shown"])["line"].replace("Delegator", "<title>")
                   .replace("Level 3 of", "Level <L> of").replace("Level 3 or", "Level <L> or"))
        not_enough = overall([2, "not_shown", "not_shown", "not_shown", 1])["line"].replace("only 2", "only <n>")
        for name in ("assess-my-ai-work", "assess-my-chats"):
            body = re.sub(r"\s+", " ", (skills / name / "SKILL.md").read_text())
            with self.subTest(name):
                self.assertIn(generic, body)
                self.assertIn(not_enough, body)
                self.assertIn(lines[1], body)
                self.assertIn("at least 3 of the 5 capabilities have a", body)
                self.assertIn("Level 1 Explorer, Level 2 Practitioner, Level 3 Delegator, Level 4 Orchestrator", body)
        self.assertIn(lines[0], re.sub(r"\s+", " ", (skills / "assess-my-ai-work" / "SKILL.md").read_text()))

    def test_assess_reports_the_overall_level(self):
        out = assess({"user_messages": 7, "runs": [RUN] * 3})
        levels = [out["capabilities"][c]["level"] for c in Coverage.NAMES]
        self.assertEqual(out["overall"], overall(levels))
        self.assertIsNotNone(out["overall"]["level"])


if __name__ == "__main__":
    unittest.main()
