"""python3 -m unittest scripts/test_record_contract.py

Ticket 35, D7 and D13: the machine-readable record does not change. The title,
Proven levels, task range and reuse are for people only. These tests pin the
contract as it stood on main at 07fc233, which modo-mcp reads.
"""

import hashlib
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from aggregate_chats import aggregate  # noqa: E402
from test_aggregate_chats import chat_levels  # noqa: E402
from validate_assessment_record import validate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "modo-ai-skills" / "skills"
FIXTURE = ROOT / "scripts" / "fixtures" / "records" / "valid-multi-chat.json"
# sha256 of each file at 07fc233. A change here is a change to what modo-mcp reads.
PINNED = {
    "plugins/modo-ai-skills/skills/export-assessment/RECORD.md":
        "f01e5961a86c111d8d7450b58eadfc28a5b04c78a2588eba800f678c16852d58",
    "plugins/modo-ai-skills/skills/save-to-passport/RECORD.md":
        "f01e5961a86c111d8d7450b58eadfc28a5b04c78a2588eba800f678c16852d58",
    "plugins/modo-ai-skills/skills/export-assessment/assessment-record.schema.json":
        "8909b2af9b88dbbac1cc6a20e2c7d60f5f4e6d1067cb629b886d323f37a56943",
    "plugins/modo-ai-skills/skills/save-to-passport/assessment-record.schema.json":
        "8909b2af9b88dbbac1cc6a20e2c7d60f5f4e6d1067cb629b886d323f37a56943",
    "scripts/validate_assessment_record.py":
        "4aa3116e4c37cd651f5d79bfe7014ab4b7e7eba1f69691bd90f7d96900c2cc7c",
}
# Fields this build added for people; none may reach a record.
PEOPLE_ONLY = ("chat_titles", "proven", "person", "task_range", "reuse", "agent_session", "task_type", "overall")


def shape(value):
    """The record's shape, key order included, with lists reduced to their first
    item. Leaf types are the validator's job (a level is an integer or a word)."""
    if isinstance(value, dict):
        return [[k, shape(v)] for k, v in value.items()]
    if isinstance(value, list):
        return [shape(value[0])] if value else []
    return "value"


def record_from(out, results):
    """The multi-chat record export-assessment builds from a result, as RECORD.md
    says: the listed fields only, in their order."""
    chats = []
    for i, r in enumerate(sorted(results, key=lambda x: x["updated_at"], reverse=True), 1):
        chats.append({"title": f"Chat {i}", "date": r["updated_at"][:10], "result": "scored",
                      "levels": {c: v["level"] for c, v in r["capabilities"].items()}})
    return {"rubric_version": "v1.1", "scope": "multi_chat", "capabilities": out["capabilities"], "evidence": [],
            "session_title": f"Assessment across {len(results)} chats",
            "session_date": out["chats_assessed"]["to"], "chats_assessed": out["chats_assessed"],
            "chats": chats, "coverage": out["coverage"]}


class RecordContract(unittest.TestCase):
    def test_contract_files_are_the_ones_on_main(self):
        for rel, want in PINNED.items():
            with self.subTest(rel):
                self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), want)

    def build(self):
        results = [chat_levels(i, [3, 4, 2, 3, "not_shown"], agent=i % 2 == 0) for i in range(1, 13)]
        results.append(chat_levels(14, [5, 4, 2, 4, "not_shown"], agent=True))
        out = aggregate(results)
        return out, record_from(out, results)

    def test_a_record_from_this_build_passes_the_validator(self):
        self.assertEqual(validate(self.build()[1]), [])

    def test_its_shape_is_the_valid_fixtures_shape(self):
        want = json.loads(FIXTURE.read_text())
        want["evidence"] = []
        got = self.build()[1]
        self.assertEqual([k for k, _ in shape(got)], [k for k, _ in shape(want)])
        cap = next(c for c in want["capabilities"].values() if c["best_shown"] is not None and c["trend"])
        got_cap = got["capabilities"]["problem_solving"]
        self.assertEqual(shape(got_cap), shape(cap))
        self.assertEqual(list(got["chats_assessed"]), list(want["chats_assessed"]))
        self.assertEqual(shape(got["chats"]), shape(want["chats"]))

    def test_best_shown_keeps_its_two_chat_rule_in_the_record(self):
        out = aggregate([chat_levels(1, [4, 3, 2, 2, 2]), chat_levels(2, [4, 3, 2, 2, 2]),
                         chat_levels(3, [2, 3, 2, 2, 2])])
        self.assertEqual(out["capabilities"]["problem_solving"]["best_shown"], 4)
        self.assertEqual(out["proven"]["problem_solving"], 2)

    def test_no_people_only_field_is_in_the_record(self):
        text = json.dumps(self.build()[1])
        for key in PEOPLE_ONLY:
            with self.subTest(key):
                self.assertNotIn(f'"{key}"', text)

    def test_the_record_refuses_a_title(self):
        record = self.build()[1]
        record["person"] = {"title": "Delegator"}
        self.assertTrue(any("person" in e for e in validate(record)))


if __name__ == "__main__":
    unittest.main()
