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
from validate_assessment_record import extract_block, validate  # noqa: E402

LABEL = "Self-assessment by Claude using Modo rubric v1 — not verified."

GOOD = {
    "rubric_version": "v1",
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


class Docs(unittest.TestCase):
    def test_example_in_record_md_is_valid(self):
        section = (SKILL / "RECORD.md").read_text().split("## Example")[1]
        record = extract_block(section.split("\n```\n")[0] + "\n```\n")
        self.assertEqual(validate(record), [])

    def test_schema_states_the_same_limits(self):
        s = json.loads((SKILL / "assessment-record.schema.json").read_text())
        item = s["properties"]["evidence"]
        self.assertEqual(item["maxItems"], 5)
        self.assertEqual(item["items"]["properties"]["quote"]["maxLength"], 240)
        self.assertEqual(s["properties"]["session_title"]["maxLength"], 120)
        self.assertEqual(sorted(s["properties"]["capabilities"]["required"]),
                         sorted(GOOD["capabilities"]))
        self.assertFalse(s["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
