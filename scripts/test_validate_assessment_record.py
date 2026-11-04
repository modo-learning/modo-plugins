"""python3 -m unittest scripts/test_validate_assessment_record.py

Expected values are written out by hand from SPEC-modo-ai-skills.md
("Assessment record"), not recomputed with the validator's own constants.
"""

import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate_assessment_record import extract_block, last_json_block, validate  # noqa: E402

LABEL = "Self-assessment by Claude using Modo rubric v1.2 — not verified."

GOOD = {
    "rubric_version": "v1.2",
    "capabilities": {
        "problem_solving": {"level": 4, "confidence": "medium"},
        "verification": {"level": 5, "confidence": "high"},
        "workflow_design": {"level": 2, "confidence": "medium"},
        "delegation": {"level": 1, "confidence": "low"},
        "strategic_thinking": {"level": "not_shown", "confidence": "low"},
    },
    "evidence": [
        {"capability": "verification", "quote": "Team is 310 against 280, which is 10.7%, not 14.3%."},
    ],
    "session_title": "Q3 pricing analysis for the board",
    "session_date": "2026-10-20",
}


def variant(**changes):
    r = copy.deepcopy(GOOD)
    r.update(changes)
    return r


def with_cap(name, **entry):
    r = copy.deepcopy(GOOD)
    r["capabilities"][name] = entry
    return r


class Validate(unittest.TestCase):
    def test_good_record_passes(self):
        self.assertEqual(validate(GOOD), [])

    def test_scores_only_passes(self):
        self.assertEqual(validate(variant(evidence=[])), [])

    def test_unknown_top_level_field_rejected(self):
        self.assertTrue(validate(variant(transcript="hello")))

    def test_missing_field_rejected(self):
        r = copy.deepcopy(GOOD)
        del r["session_date"]
        self.assertTrue(validate(r))

    def test_wrong_capability_set_rejected(self):
        r = copy.deepcopy(GOOD)
        del r["capabilities"]["delegation"]
        self.assertTrue(validate(r))
        r = copy.deepcopy(GOOD)
        r["capabilities"]["creativity"] = {"level": 3, "confidence": "low"}
        self.assertTrue(validate(r))

    def test_level_range(self):
        for bad in (0, 6, 3.5, "3", True, None, "Not shown"):
            self.assertTrue(validate(with_cap("verification", level=bad, confidence="low")), bad)
        for ok in (1, 2, 3, 4, 5):
            self.assertEqual(validate(with_cap("verification", level=ok, confidence="low")), [], ok)

    def test_level_written_as_1_point_0_rejected(self):
        # JSON Schema's "integer" accepts 1.0; the validator, which RECORD.md
        # makes authoritative, does not: a level is written as a bare integer.
        text = json.dumps(GOOD).replace('"level": 4', '"level": 4.0', 1)
        self.assertIn('"level": 4.0', text)
        self.assertTrue(validate(json.loads(text)))

    def test_confidence_values(self):
        self.assertTrue(validate(with_cap("verification", level=3, confidence="certain")))
        self.assertTrue(validate(with_cap("verification", level=3)))

    def test_unknown_field_inside_capability_rejected(self):
        self.assertTrue(validate(with_cap("verification", level=3, confidence="low", note="x")))

    def test_rubric_version_format(self):
        self.assertTrue(validate(variant(rubric_version="1")))
        self.assertTrue(validate(variant(rubric_version="")))
        self.assertEqual(validate(variant(rubric_version="v2")), [])

    def test_minor_rubric_version_accepted(self):
        for known in ("v1", "v1.1", "v1.2"):
            self.assertEqual(validate(variant(rubric_version=known)), [])
        for bad in ("v1.", "v1.2.1", "v.1", "1.1"):
            self.assertTrue(validate(variant(rubric_version=bad)), bad)

    def test_evidence_count_limit(self):
        item = {"capability": "verification", "quote": "q"}
        self.assertEqual(validate(variant(evidence=[item] * 5)), [])
        self.assertTrue(validate(variant(evidence=[item] * 6)))

    def test_quote_length_limit(self):
        def ev(n):
            return variant(evidence=[{"capability": "verification", "quote": "a" * n}])
        self.assertEqual(validate(ev(240)), [])
        self.assertTrue(validate(ev(241)))
        self.assertTrue(validate(ev(0)))

    def test_quote_length_counts_characters_not_bytes(self):
        r = variant(evidence=[{"capability": "verification", "quote": "é" * 240}])
        self.assertEqual(validate(r), [])

    def test_evidence_must_name_one_of_the_five(self):
        self.assertTrue(validate(variant(evidence=[{"capability": "luck", "quote": "q"}])))
        self.assertTrue(validate(variant(evidence=[{"quote": "q"}])))

    def test_evidence_unknown_field_rejected(self):
        self.assertTrue(validate(variant(evidence=[{"capability": "verification", "quote": "q", "message_id": 3}])))

    def test_title_limit(self):
        self.assertEqual(validate(variant(session_title="t" * 120)), [])
        self.assertTrue(validate(variant(session_title="t" * 121)))
        self.assertTrue(validate(variant(session_title="")))

    def test_date_must_be_iso_date(self):
        for bad in ("20/10/2026", "2026-13-01", "2026-02-30", "2026-10-20T10:00:00Z", "", None, 20261020):
            self.assertTrue(validate(variant(session_date=bad)), bad)
        self.assertEqual(validate(variant(session_date="2026-02-28")), [])

    def test_not_a_dict(self):
        self.assertTrue(validate([]))

    # Plugin conventions (RECORD.md), on by default, off with convention=False.
    def test_not_shown_must_record_low_confidence(self):
        r = with_cap("strategic_thinking", level="not_shown", confidence="high")
        self.assertTrue(validate(r))
        self.assertEqual(validate(r, convention=False), [])

    def test_no_quote_for_a_not_shown_capability(self):
        r = variant(evidence=[{"capability": "strategic_thinking", "quote": "q"}])
        self.assertTrue(validate(r))
        self.assertEqual(validate(r, convention=False), [])


# A multi-chat record, worked out by hand from the aggregation rules in
# Modo workspace doc docs/ai-skills/DESIGN-multi-chat-assessment.md (not in this repo),
# "Aggregation rules". Chats newest first:
#   1 2026-10-30 scored     P3 V4 W2 D- S-
#   2 2026-10-27 scored     P3 V4 W4 D4 S-
#   3 2026-10-21 too short
#   4 2026-10-14 scored     P2 V3 W2 D3 S-
#   5 2026-10-06 scored     P2 V3 W- D2 S-
# P: 2,2,3,3 -> level 2 (lower middle), best 3, high (4 chats, spread 1), up.
# V: 3,3,4,4 -> level 3, best 4, high, up.
# W: 2,4,2 (oldest first) -> level 2, best 2, medium (3 chats, spread 2), no trend.
# D: 2,3,4 -> level 3, no best (no level twice), medium, no trend.
# S: not shown. Coverage 4.
def _levels(p, v, w, d, s):
    return dict(zip(("problem_solving", "verification", "workflow_design", "delegation",
                     "strategic_thinking"), (p, v, w, d, s)))


NS = "not_shown"
MULTI = {
    "rubric_version": "v1.2",
    "scope": "multi_chat",
    "capabilities": {
        "problem_solving": {"level": 2, "confidence": "high", "best_shown": 3, "trend": "up", "chats_shown": 4},
        "verification": {"level": 3, "confidence": "high", "best_shown": 4, "trend": "up", "chats_shown": 4},
        "workflow_design": {"level": 2, "confidence": "medium", "best_shown": 2, "trend": None, "chats_shown": 3},
        "delegation": {"level": 3, "confidence": "medium", "best_shown": None, "trend": None, "chats_shown": 3},
        "strategic_thinking": {"level": NS, "confidence": "low", "best_shown": None, "trend": None, "chats_shown": 0},
    },
    "evidence": [
        {"capability": "verification", "chat": 4,
         "quote": "Before we use that number, show me the query you ran so I can rerun it."},
    ],
    "session_title": "Assessment across 4 chats",
    "session_date": "2026-10-30",
    "chats_assessed": {"count": 5, "scored": 4, "too_short": 1, "could_not_be_read": 0,
                       "from": "2026-10-06", "to": "2026-10-30"},
    "chats": [
        {"title": "Chat 1", "date": "2026-10-30", "result": "scored", "levels": _levels(3, 4, 2, NS, NS)},
        {"title": "Chat 2", "date": "2026-10-27", "result": "scored", "levels": _levels(3, 4, 4, 4, NS)},
        {"title": "Chat 3", "date": "2026-10-21", "result": "too_short", "levels": None},
        {"title": "Chat 4", "date": "2026-10-14", "result": "scored", "levels": _levels(2, 3, 2, 3, NS)},
        {"title": "Chat 5", "date": "2026-10-06", "result": "scored", "levels": _levels(2, 3, NS, 2, NS)},
    ],
    "coverage": 4,
}


def multi(**changes):
    r = copy.deepcopy(MULTI)
    r.update(changes)
    return r


def record_from_results(results):
    """A multi-chat record built the way the skill builds it: aggregate() over the
    ChatResults, chats newest first by updated_at."""
    from aggregate_chats import aggregate
    out = aggregate(results)
    newest = sorted(results, key=lambda r: r["updated_at"], reverse=True)
    chats = [{"title": f"Chat {i}", "date": r["updated_at"][:10],
              "result": "too_short" if r["too_short"] else "scored",
              "levels": None if r["too_short"] else {k: c["level"] for k, c in r["capabilities"].items()}}
             for i, r in enumerate(newest, 1)]
    return {"rubric_version": "v1.2", "scope": "multi_chat", "capabilities": out["capabilities"],
            "evidence": [], "session_title": "Assessment across chats",
            "session_date": out["chats_assessed"]["to"], "chats_assessed": out["chats_assessed"],
            "chats": chats, "coverage": out["coverage"]}


class SameArithmeticAsAggregate(unittest.TestCase):
    def test_a_record_built_from_aggregate_is_valid(self):
        from test_aggregate_chats import chat
        results = [chat(1, 3), chat(5, 2), chat(5, 4), chat(9, 3), chat(12, 4, user_messages=2)]
        results[2]["updated_at"] = "2026-10-05T18:00:00Z"   # same day as chat(5, 2), later
        record = record_from_results(results)
        # Oldest first by time: 3, 2, 4, 3 -> earlier half 2, later half 3: up.
        self.assertEqual(record["capabilities"]["verification"]["trend"], "up")
        self.assertEqual(validate(record), [])

    def test_trend_follows_the_dates(self):
        from test_aggregate_chats import chat
        record = record_from_results([chat(1, 4), chat(3, 4), chat(6, 2), chat(8, 2)])
        self.assertEqual(record["capabilities"]["verification"]["trend"], "down")
        self.assertEqual(validate(record), [])
        record["capabilities"]["verification"]["trend"] = "up"
        self.assertIn("capabilities.verification.trend: is 'up', the per-chat levels give 'down'", validate(record))


class ValidateMultiChat(unittest.TestCase):
    def test_good_multi_chat_record_passes(self):
        self.assertEqual(validate(MULTI), [])

    def test_absent_scope_is_a_single_chat_record(self):
        # Single-chat records stay exactly as they were: no scope, none of the multi-chat fields.
        self.assertEqual(validate(GOOD), [])
        self.assertTrue(validate(variant(chats=MULTI["chats"])))
        self.assertTrue(validate(variant(coverage=4)))

    def test_scope_value(self):
        for bad in ("single_chat", "multi", "", None):
            self.assertTrue(validate(multi(scope=bad)), bad)

    def test_multi_chat_fields_are_required(self):
        for field in ("chats_assessed", "chats", "coverage", "session_title", "session_date"):
            r = copy.deepcopy(MULTI)
            del r[field]
            self.assertTrue(validate(r), field)

    def test_unknown_field_rejected(self):
        self.assertTrue(validate(multi(transcript="hello")))
        r = copy.deepcopy(MULTI)
        r["chats"][0]["quotes"] = ["q"]
        self.assertTrue(validate(r))
        r = copy.deepcopy(MULTI)
        r["chats_assessed"]["skipped"] = 2
        self.assertTrue(validate(r))
        r = copy.deepcopy(MULTI)
        r["capabilities"]["verification"]["agreement"] = "3 of 3 runs"
        self.assertTrue(validate(r))

    def test_rubric_version_stays_v1_1_format(self):
        self.assertTrue(validate(multi(rubric_version="1.1")))

    def test_counts_must_add_up(self):
        r = copy.deepcopy(MULTI)
        r["chats_assessed"]["count"] = 6
        self.assertTrue(validate(r))
        r = copy.deepcopy(MULTI)
        r["chats_assessed"]["too_short"] = 0
        self.assertTrue(validate(r))

    def test_counts_match_the_per_chat_results(self):
        r = copy.deepcopy(MULTI)
        r["chats"][2] = {"title": "Chat 3", "date": "2026-10-21", "result": "could_not_be_read", "levels": None}
        self.assertTrue(validate(r))
        r["chats_assessed"].update(too_short=0, could_not_be_read=1)
        self.assertEqual(validate(r), [])

    def test_at_least_one_scored_chat(self):
        r = copy.deepcopy(MULTI)
        for c in r["chats"]:
            c.update(result="too_short", levels=None)
        r["chats_assessed"].update(scored=0, too_short=5)
        self.assertTrue(validate(r))

    def test_at_most_25_chats(self):
        r = copy.deepcopy(MULTI)
        extra = [{"title": f"Chat {n}", "date": "2026-10-01", "result": "too_short", "levels": None}
                 for n in range(6, 27)]
        r["chats"] += extra
        r["chats_assessed"].update(count=26, too_short=22)
        self.assertTrue(validate(r))
        r["chats"].pop()
        r["chats_assessed"].update(count=25, too_short=21)
        self.assertEqual(validate(r), [])

    def test_date_range_is_the_scored_chats(self):
        r = copy.deepcopy(MULTI)
        r["chats_assessed"]["from"] = "2026-10-01"
        self.assertTrue(validate(r))
        r = copy.deepcopy(MULTI)
        r["chats_assessed"]["to"] = "2026-10-31"
        r["session_date"] = "2026-10-31"
        self.assertTrue(validate(r))
        r = copy.deepcopy(MULTI)
        r["chats_assessed"]["to"] = "2026-02-30"
        self.assertTrue(validate(r))

    def test_session_date_is_the_newest_scored_chat(self):
        self.assertTrue(validate(multi(session_date="2026-11-02")))

    def test_chats_newest_first(self):
        r = copy.deepcopy(MULTI)
        r["chats"][0], r["chats"][1] = r["chats"][1], r["chats"][0]
        self.assertTrue(validate(r))

    def test_per_chat_fields(self):
        for change in ({"title": ""}, {"title": "t" * 121}, {"date": "30/10/2026"},
                       {"result": "skipped"}, {"levels": None}):
            r = copy.deepcopy(MULTI)
            r["chats"][0].update(change)
            self.assertTrue(validate(r), change)
        r = copy.deepcopy(MULTI)
        r["chats"][2]["levels"] = _levels(1, 1, 1, 1, 1)
        self.assertTrue(validate(r))
        r = copy.deepcopy(MULTI)
        r["chats"][0]["levels"]["verification"] = 6
        self.assertTrue(validate(r))

    def test_approved_chat_title_allowed(self):
        r = copy.deepcopy(MULTI)
        r["chats"][0]["title"] = "CSV merge drops rows"
        self.assertEqual(validate(r), [])

    def test_combined_levels_must_follow_the_aggregation_rules(self):
        for cap, field, bad in (("problem_solving", "level", 3), ("verification", "confidence", "medium"),
                                ("verification", "best_shown", 3), ("problem_solving", "trend", "flat"),
                                ("delegation", "trend", "up"), ("workflow_design", "chats_shown", 4),
                                ("delegation", "best_shown", 3)):
            r = copy.deepcopy(MULTI)
            r["capabilities"][cap][field] = bad
            self.assertTrue(validate(r), (cap, field, bad))

    def test_combined_field_values(self):
        for field, bad in (("best_shown", 6), ("best_shown", "3"), ("trend", "sideways"),
                           ("chats_shown", -1), ("chats_shown", True)):
            r = copy.deepcopy(MULTI)
            r["capabilities"]["verification"][field] = bad
            self.assertTrue(validate(r), (field, bad))

    def test_coverage_counts_shown_capabilities(self):
        self.assertTrue(validate(multi(coverage=5)))
        self.assertTrue(validate(multi(coverage="4")))

    def test_evidence_names_a_scored_chat_that_shows_the_capability(self):
        for chat in (0, 6, 3, "4", None):  # 3 is too short
            r = copy.deepcopy(MULTI)
            r["evidence"][0]["chat"] = chat
            self.assertTrue(validate(r), chat)
        r = copy.deepcopy(MULTI)
        del r["evidence"][0]["chat"]
        self.assertTrue(validate(r))

    def test_evidence_limits_unchanged(self):
        item = {"capability": "verification", "chat": 4, "quote": "q"}
        self.assertEqual(validate(multi(evidence=[item] * 5)), [])
        self.assertTrue(validate(multi(evidence=[item] * 6)))
        self.assertTrue(validate(multi(evidence=[dict(item, quote="a" * 241)])))
        self.assertEqual(validate(multi(evidence=[])), [])

    # Convention (RECORD.md): a quote comes from a chat whose level equals the combined level.
    def test_quote_from_a_chat_at_the_combined_level(self):
        r = copy.deepcopy(MULTI)
        r["evidence"][0]["chat"] = 1  # verification 4 there, combined 3
        self.assertTrue(validate(r))
        self.assertEqual(validate(r, convention=False), [])

    def test_a_single_chat_record_cannot_name_a_chat(self):
        self.assertTrue(validate(variant(evidence=[{"capability": "verification", "chat": 1, "quote": "q"}])))


def report(block, tail=""):
    return "# Report\n\nSome text.\n\n```json\n" + block + "\n```\n" + tail


class Extract(unittest.TestCase):
    def test_block_at_end(self):
        self.assertEqual(extract_block(report(json.dumps(GOOD, indent=2))), GOOD)

    def test_label_after_block_allowed(self):
        self.assertEqual(extract_block(report(json.dumps(GOOD), "\n" + LABEL + "\n")), GOOD)

    def test_text_after_block_rejected(self):
        with self.assertRaises(ValueError):
            extract_block(report(json.dumps(GOOD), "\nMore words.\n"))

    def test_no_block(self):
        with self.assertRaises(ValueError):
            extract_block("just text, no block")

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            extract_block(report("{not json"))

    def test_last_json_block_is_the_record(self):
        text = report('{"a": 1}') + "\nmore\n\n" + report(json.dumps(GOOD))
        self.assertEqual(extract_block(text), GOOD)

    def test_other_fences_ignored(self):
        text = report(json.dumps(GOOD)).replace("Some text.", "```\ncode\n```")
        self.assertEqual(extract_block(text), GOOD)


SKILL = pathlib.Path(__file__).parent.parent / "plugins" / "modo-ai-skills" / "skills" / "export-assessment"


class LastJsonBlock(unittest.TestCase):
    """A chat reply that shows a record and then asks a question."""

    def test_question_may_follow_the_block(self):
        text = report(json.dumps(GOOD), "\nSay \"send it\" to save exactly this record.\n")
        self.assertEqual(last_json_block(text), GOOD)

    def test_last_of_two_blocks(self):
        text = report(json.dumps({"a": 1})) + report(json.dumps(GOOD), "\nOK?\n")
        self.assertEqual(last_json_block(text), GOOD)

    def test_none_without_a_block_or_with_bad_json(self):
        self.assertIsNone(last_json_block("no block"))
        self.assertIsNone(last_json_block(None))
        self.assertIsNone(last_json_block(report("{not json", "\nOK?\n")))


class Docs(unittest.TestCase):
    def example(self, heading):
        section = (SKILL / "RECORD.md").read_text().split(heading + "\n")[1]
        return extract_block(section.split("\n```\n")[0] + "\n```\n")

    def test_example_in_record_md_is_valid(self):
        record = self.example("## Example")
        self.assertNotIn("scope", record)
        self.assertEqual(validate(record), [])

    def test_multi_chat_example_in_record_md_is_valid(self):
        record = self.example("### Multi-chat example")
        self.assertEqual(record["scope"], "multi_chat")
        self.assertEqual(record["rubric_version"], "v1.2")
        self.assertEqual(validate(record), [])

    def schema(self):
        return json.loads((SKILL / "assessment-record.schema.json").read_text())

    def test_schema_states_the_same_limits(self):
        s = self.schema()
        for branch in ("single_chat", "multi_chat"):
            b = s["$defs"][branch]
            item = b["properties"]["evidence"]
            self.assertEqual(item["maxItems"], 5, branch)
            self.assertEqual(item["items"]["properties"]["quote"]["maxLength"], 240, branch)
            self.assertEqual(b["properties"]["session_title"]["maxLength"], 120, branch)
            self.assertEqual(sorted(b["properties"]["capabilities"]["required"]),
                             sorted(GOOD["capabilities"]), branch)
            self.assertFalse(b["additionalProperties"], branch)
        self.assertEqual(sorted(r["$ref"] for r in s["oneOf"]),
                         ["#/$defs/multi_chat", "#/$defs/single_chat"])

    def test_schema_fields_match_the_validator(self):
        s = self.schema()["$defs"]
        self.assertEqual(sorted(s["single_chat"]["required"]), sorted(GOOD))
        self.assertNotIn("scope", s["single_chat"]["properties"])
        self.assertEqual(sorted(s["multi_chat"]["required"]), sorted(MULTI))
        self.assertEqual(s["multi_chat"]["properties"]["scope"], {"const": "multi_chat"})
        self.assertEqual(s["multi_chat"]["properties"]["chats"]["maxItems"], 25)
        self.assertEqual(sorted(s["multi_capability"]["required"]),
                         sorted(MULTI["capabilities"]["verification"]))
        self.assertEqual(sorted(s["multi_chat"]["properties"]["chats_assessed"]["required"]),
                         sorted(MULTI["chats_assessed"]))
        self.assertEqual(sorted(s["chat_summary"]["required"]), sorted(MULTI["chats"][0]))


RECORDS = pathlib.Path(__file__).parent / "fixtures" / "records"


class ExampleRecords(unittest.TestCase):
    """fixtures/records: valid-*.json pass; invalid-*.json fail with the error named in "_expect"."""

    def test_valid_examples_pass(self):
        files = sorted(RECORDS.glob("valid-*.json"))
        self.assertTrue(files)
        for f in files:
            self.assertEqual(validate(json.loads(f.read_text())), [], f.name)

    def test_invalid_examples_fail_for_the_stated_reason(self):
        files = sorted(RECORDS.glob("invalid-*.json"))
        self.assertTrue(files)
        for f in files:
            case = json.loads(f.read_text())
            errors = validate(case["record"])
            self.assertTrue(any(case["expect"] in e for e in errors), (f.name, errors))


if __name__ == "__main__":
    unittest.main()
