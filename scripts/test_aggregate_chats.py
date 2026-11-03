"""python3 -m unittest scripts/test_aggregate_chats.py

The worked examples below are the table to show when the rules are reviewed:
each row is per-chat levels (oldest first) -> level, best, confidence, trend.
"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from aggregate_chats import aggregate, lower_median  # noqa: E402
from validate_chat_result import CAPABILITIES, validate  # noqa: E402


def chat(day, verification="not_shown", user_messages=6):
    too_short = user_messages < 4
    caps = {}
    for cap in CAPABILITIES:
        level = verification if cap == "verification" and not too_short else "not_shown"
        shown = level != "not_shown"
        caps[cap] = {"level": level, "confidence": "medium" if shown else "low",
                     "agreement": "" if too_short else "3 of 3 runs",
                     "behaviours": [f"V{level}a"] if shown and level != 1 else (["V1"] if shown else []),
                     "quotes": [{"message": 1, "text": "check it"}] if shown else []}
    return {"chat_id": f"c{day}", "title": f"chat {day}", "updated_at": f"2026-10-{day:02d}T10:00:00Z",
            "turns_total": user_messages * 2, "user_messages": user_messages, "unreadable_turns": 0,
            "attachments_seen": False, "truncated_turns": [], "too_short": too_short,
            "runs": 0 if too_short else 3, "run_kind": "none" if too_short else "one_response",
            "capabilities": caps}


# levels oldest first -> (level, best_shown, confidence, trend)
WORKED = [
    ([3], (3, None, "low", None)),
    ([3, 4], (3, None, "medium", None)),
    ([2, 4], (2, None, "low", None)),
    ([3, 3, 4], (3, 3, "high", None)),
    ([2, 3, 4], (3, None, "medium", None)),
    ([1, 3, 5], (3, None, "low", None)),
    ([2, 2, 4, 4], (2, 4, "medium", "up")),
    ([4, 4, 3, 3], (3, 4, "high", "down")),
    ([3, 3, 3, 3, 3], (3, 3, "high", "flat")),
    ([2, 3, 5, 4, 4], (4, 4, "low", "up")),
]


class WorkedExamples(unittest.TestCase):
    def test_the_worked_examples_table(self):
        for levels, (level, best, confidence, trend) in WORKED:
            with self.subTest(levels=levels):
                results = [chat(i + 1, lvl) for i, lvl in enumerate(levels)]
                for r in results:
                    self.assertEqual(validate(r), [])
                v = aggregate(results)["capabilities"]["verification"]
                self.assertEqual((v["level"], v["best_shown"], v["confidence"], v["trend"]),
                                 (level, best, confidence, trend))
                self.assertEqual(v["chats_shown"], len(levels))

    def test_trend_uses_dates_not_list_order(self):
        results = [chat(20, 4), chat(1, 2), chat(25, 4), chat(5, 2)]
        self.assertEqual(aggregate(results)["capabilities"]["verification"]["trend"], "up")


def chat_levels(day, levels):
    """A scored chat with the five levels given in rubric order."""
    r = chat(day, levels[1])
    for cap, level in zip(CAPABILITIES, levels):
        shown = level != "not_shown"
        letter = cap[0].upper()
        r["capabilities"][cap] = {"level": level, "confidence": "medium" if shown else "low",
                                  "agreement": "3 of 3 runs",
                                  "behaviours": ([f"{letter}{level}a"] if level != 1 else [f"{letter}1"]) if shown else [],
                                  "quotes": [{"message": 1, "text": "check it"}] if shown else []}
    return r


class Overall(unittest.TestCase):
    """The overall AI fluency level comes from the combined levels (derive_levels.overall).
    It is a derived value in this output only; the record does not store it."""

    def test_overall_from_the_combined_levels(self):
        # Combined: P 4, V 3, W 3, D 2, S not shown -> 3 capabilities at 3 or higher.
        results = [chat_levels(1, [4, 3, 3, 2, "not_shown"]), chat_levels(2, [4, 4, 3, 2, "not_shown"]),
                   chat_levels(3, [5, 3, 2, 2, "not_shown"])]
        for r in results:
            self.assertEqual(validate(r), [])
        out = aggregate(results)
        self.assertEqual([out["capabilities"][c]["level"] for c in CAPABILITIES], [4, 3, 3, 2, "not_shown"])
        self.assertEqual((out["overall"]["level"], out["overall"]["title"]), (3, "Delegator"))

    def test_no_overall_when_fewer_than_3_are_shown(self):
        out = aggregate([chat(1, 4), chat(2, 4)])
        self.assertEqual((out["overall"]["level"], out["overall"]["title"]), (None, None))


class Counting(unittest.TestCase):
    def test_too_short_chats_are_listed_but_not_scored(self):
        results = [chat(1, 3), chat(2, 4, user_messages=2), chat(3, 3)]
        out = aggregate(results)
        self.assertEqual(out["chats_assessed"], {"count": 3, "scored": 2, "too_short": 1, "could_not_be_read": 0,
                                                 "from": "2026-10-01", "to": "2026-10-03"})
        self.assertEqual(out["capabilities"]["verification"]["chats_shown"], 2)

    def test_failed_reads_count_as_could_not_be_read_not_too_short(self):
        # What an agent returns when the tool fails or the chat is flagged (brief, step 1).
        failed = {"chat_id": "c9", "error": "tool error"}
        out = aggregate([chat(1, 3), failed, chat(2, 4, user_messages=2), None])
        self.assertEqual(out["chats_assessed"], {"count": 4, "scored": 1, "too_short": 1, "could_not_be_read": 2,
                                                 "from": "2026-10-01", "to": "2026-10-01"})
        self.assertEqual(out["capabilities"]["verification"]["level"], 3)

    def test_counts_use_the_records_names(self):
        from validate_assessment_record import ASSESSED_FIELDS
        self.assertEqual(set(aggregate([chat(1, 3)])["chats_assessed"]), ASSESSED_FIELDS)

    def test_not_shown_anywhere(self):
        out = aggregate([chat(1), chat(2)])
        self.assertEqual(out["capabilities"]["verification"],
                         {"level": "not_shown", "confidence": "low", "best_shown": None, "trend": None,
                          "chats_shown": 0})
        self.assertEqual(out["coverage"], 0)

    def test_coverage_counts_capabilities_shown_at_least_once(self):
        self.assertEqual(aggregate([chat(1, 3), chat(2)])["coverage"], 1)

    def test_no_chats(self):
        out = aggregate([])
        a = out["chats_assessed"]
        self.assertEqual((a["scored"], a["from"], a["to"], out["coverage"]), (0, None, None, 0))

    def test_lower_median(self):
        self.assertEqual([lower_median(x) for x in ([1], [1, 2], [1, 2, 3], [4, 1, 3, 2])], [1, 1, 2, 2])


if __name__ == "__main__":
    unittest.main()
