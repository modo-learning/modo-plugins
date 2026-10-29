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
from derive_levels import BEHAVIOURS, combine, coverage, derive  # noqa: E402

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
                         {"level": "not shown", "confidence": None, "agreement": "runs disagreed"})

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

    def test_three_or_fewer_is_partial(self):
        self.assertEqual(coverage(self.levels(3, "not shown", 2, "not shown", "not shown")),
                         "This chat shows only 2 of 5 capabilities, so this is a partial picture. "
                         "Assess 2–3 more chats with different kinds of work to see the rest.")


if __name__ == "__main__":
    unittest.main()
