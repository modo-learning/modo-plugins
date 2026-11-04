"""python3 -m unittest scripts/test_aggregate_chats.py

The worked examples below are the table to show when the rules are reviewed:
each row is per-chat levels (oldest first) -> level, best, confidence, trend.
"""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from aggregate_chats import aggregate, lower_median  # noqa: E402
from validate_chat_result import CAPABILITIES, validate  # noqa: E402


def chat(day, verification="not_shown", user_messages=6, agent=False, task="Coding", reused=False):
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
            "agent_session": {"value": bool(agent) and not too_short, "quote": None,
                              "tools": ["Bash", "Edit"] if agent and not too_short else []},
            "task_type": None if too_short else task,
            "reuse": {"value": reused and not too_short,
                      "quote": {"message": 1, "text": "use my usual format"} if reused and not too_short else None},
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


def person_title(out):
    return out["person"]["title"]


def chat_levels(day, levels, agent=False):
    """A scored chat with the five levels given in rubric order."""
    r = chat(day, levels[1], agent=agent)
    for cap, level in zip(CAPABILITIES, levels):
        shown = level != "not_shown"
        letter = cap[0].upper()
        r["capabilities"][cap] = {"level": level, "confidence": "medium" if shown else "low",
                                  "agreement": "3 of 3 runs",
                                  "behaviours": ([f"{letter}{level}a"] if level != 1 else [f"{letter}1"]) if shown else [],
                                  "quotes": [{"message": 1, "text": "check it"}] if shown else []}
    return r


D = [3, 3, 3, 3, 2]      # Delegator
P = [2, 2, 2, 2, 1]      # Practitioner
E = [1, 1, 1, 1, 1]      # Explorer
O = [5, 5, 5, 5, 3]      # Orchestrator scores
NONE = ["not_shown"] * 5  # shown nothing: scored, no title


def sheet(*levels, agent=False):
    """A scored chat per entry, one day apart."""
    return [chat_levels(i + 1, lv, agent=agent) for i, lv in enumerate(levels)]


class ChatTitles(unittest.TestCase):
    """Each chat's title comes from that chat alone (derive_levels.overall)."""

    def test_each_scored_chat_gets_its_title_and_others_none(self):
        results = sheet(D, P) + [chat(3, 4, user_messages=2), {"chat_id": "c9", "error": "tool error"}]
        out = aggregate(results)
        self.assertEqual([t and t["title"] for t in out["title_per_chat"]], ["Delegator", "Practitioner", None, None])

    def test_orchestrator_needs_that_chats_agent_session(self):
        out = aggregate([chat_levels(1, O, agent=False), chat_levels(2, O, agent=True)])
        self.assertEqual([t["title"] for t in out["title_per_chat"]], ["Delegator", "Orchestrator"])
        self.assertIn("no agent work visible", out["title_per_chat"][0]["note"])

    def test_a_scored_chat_with_no_title_is_still_listed(self):
        out = aggregate(sheet(NONE))
        self.assertEqual(out["title_per_chat"][0]["title"], None)
        self.assertEqual(out["title_per_chat"][0]["level"], None)


class PersonTitle(unittest.TestCase):
    """Johnny's rules, section 2, with D3 (cumulative), D4 (10 scored chats) and D10."""

    def test_johnnys_example_after_12_chats(self):
        # "Delegator in 3 chats, Practitioner in 6, Explorer in 3. Person title: Delegator."
        out = aggregate(sheet(*[D] * 3, *[P] * 6, *[E] * 3))
        self.assertEqual((out["person"]["level"], out["person"]["title"]), (3, "Delegator"))
        self.assertEqual(out["person"]["line"], "Your title: Delegator \u00b7 Level 3 (reached in at least 3 chats).")

    def test_a_higher_chat_title_counts_toward_lower_ones(self):
        # D3: 2 Orchestrator + 1 Delegator is Delegator in 3 chats.
        results = sheet(*[E] * 7, D) + [chat_levels(20, O, agent=True), chat_levels(21, O, agent=True)]
        self.assertEqual(person_title(aggregate(results)), "Delegator")

    def test_three_orchestrator_chats(self):
        results = sheet(*[P] * 7) + [chat_levels(20 + i, O, agent=True) for i in range(3)]
        self.assertEqual(person_title(aggregate(results)), "Orchestrator")

    def test_under_10_scored_chats_there_is_no_title(self):
        out = aggregate(sheet(*[D] * 8))
        self.assertEqual((out["person"]["level"], out["person"]["title"]), (None, None))
        self.assertEqual(out["person"]["line"], "8 of 10 chats to your title")

    def test_too_short_and_unread_chats_do_not_count_toward_the_10(self):
        results = sheet(*[D] * 9) + [chat(20, 3, user_messages=2), {"chat_id": "c9", "error": "tool error"}]
        self.assertEqual(aggregate(results)["person"]["line"], "9 of 10 chats to your title")

    def test_a_chat_with_no_title_counts_toward_the_10_but_adds_no_title(self):
        # D10: 8 chats that show nothing and 2 Delegator: 10 scored, no title in 3 chats.
        out = aggregate(sheet(*[NONE] * 8, D, D))
        self.assertEqual((out["person"]["title"], out["person"]["level"]), (None, None))
        self.assertEqual(out["person"]["line"], "Your title: No title yet (no title reached in 3 chats).")

    def test_exactly_10_scored_chats_show_the_title(self):
        self.assertEqual(person_title(aggregate(sheet(*[D] * 3, *[E] * 7))), "Delegator")

    def test_orchestrator_adds_the_multiplier_note(self):
        results = sheet(*[P] * 7) + [chat_levels(20 + i, O, agent=True) for i in range(3)]
        self.assertIn("Multiplier", aggregate(results)["person"]["note"])
        self.assertIsNone(aggregate(sheet(*[D] * 10))["person"]["note"])


class ProvenLevel(unittest.TestCase):
    """The highest level reached in at least 3 chats, cumulative (D3, D5)."""

    def test_a_higher_chat_counts_toward_a_lower_level(self):
        self.assertEqual(aggregate([chat(1, 4), chat(2, 4), chat(3, 5)])["proven"]["verification"], 4)

    def test_needs_3_chats(self):
        self.assertIsNone(aggregate([chat(1, 4), chat(2, 4)])["proven"]["verification"])
        self.assertIsNone(aggregate([chat(1), chat(2), chat(3)])["proven"]["verification"])

    def test_not_a_peak(self):
        self.assertEqual(aggregate([chat(1, 2), chat(2, 2), chat(3, 2), chat(4, 5)])["proven"]["verification"], 2)

    def test_the_median_stays_the_main_level(self):
        out = aggregate([chat(1, 1), chat(2, 3), chat(3, 3), chat(4, 3), chat(5, 3)])
        self.assertEqual((out["capabilities"]["verification"]["level"], out["proven"]["verification"]), (3, 3))

    def test_proven_shows_with_under_10_chats(self):
        self.assertEqual(aggregate([chat(1, 3), chat(2, 3), chat(3, 3)])["proven"]["verification"], 3)


class RangeAndReuse(unittest.TestCase):
    def test_counts_distinct_task_types_over_scored_chats(self):
        out = aggregate([chat(1, 3, task="Coding"), chat(2, 3, task="Coding"), chat(3, 3, task="Learning"),
                         chat(4, 3, user_messages=2)])
        self.assertEqual(out["task_range"], {"types": 2, "line": "Task range: 2 of 8 types"})

    def test_counts_chats_with_reuse_over_scored_chats(self):
        out = aggregate([chat(1, 3, reused=True), chat(2, 3), chat(3, 3, reused=True), chat(4, 3, user_messages=2)])
        self.assertEqual(out["reuse"], {"chats": 2, "line": "Reused saved work: 2 of 3 chats"})

    def test_no_saved_prompt_names_or_quotes_in_the_output(self):
        r = chat(1, 3)
        r["reuse"] = {"value": True, "quote": {"message": 1, "text": "ran the weekly-crm-update prompt"}}
        self.assertNotIn("weekly-crm-update", json.dumps(aggregate([r])))


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
