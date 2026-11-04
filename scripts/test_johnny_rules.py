"""python3 -m unittest scripts/test_johnny_rules.py

The title rule against Johnny's own examples ("AI Fluency Levels: scoring rules
v1", 2026-11-04, sections 1 and 4). The scores and titles below are copied from
his file, not worked out with our rule. Capabilities he gave no score for are
"not shown" here. D1 to O2 are his chat names, not behaviour ids.
"""

import sys
import pathlib
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from derive_levels import NO_AGENT_NOTE, overall  # noqa: E402

NS = "not_shown"
# name -> (Problem Solving, Verification, Workflow Design, Delegation,
#          Strategic Thinking), agent session, title, level
EXAMPLES = {
    "E1": ((1, NS, 2, 1, NS), False, "Explorer", 1),
    "E2": ((1, 1, 2, 2, NS), False, "Explorer", 1),
    "P1": ((3, NS, 2, 2, 3), False, "Practitioner", 2),
    "P2": ((3, 2, 3, 2, 3), False, "Practitioner", 2),
    "D1": ((3, 4, 5, 4, 2), False, "Delegator", 3),
    "D2": ((3, 4, 2, 3, 4), False, "Delegator", 3),
    "O1": ((5, 5, 4, 5, 3), True, "Orchestrator", 4),
    "O2": ((4, 5, 5, 5, 3), True, "Orchestrator", 4),
}
# Section "Edge cases". The first has no scores in his file: any two capabilities.
EDGE = {
    "fact-check-two-capabilities": ((NS, 5, NS, NS, 3), False, None, None),
    "great-plain-chat": ((5, 5, 5, 5, 5), False, "Delegator", 3),
    "twelve-people-claim": ((5, 5, 5, 5, 5), True, "Orchestrator", 4),
}


class JohnnysExamples(unittest.TestCase):
    def test_all_eight_examples_get_his_title(self):
        for name, (levels, agent, title, level) in EXAMPLES.items():
            with self.subTest(name):
                got = overall(list(levels), agent)
                self.assertEqual((got["title"], got["level"]), (title, level))

    def test_edge_cases(self):
        for name, (levels, agent, title, level) in EDGE.items():
            with self.subTest(name):
                got = overall(list(levels), agent)
                self.assertEqual((got["title"], got["level"]), (title, level))

    def test_d1_reaches_orchestrator_scores_so_it_carries_the_no_agent_note(self):
        got = overall(list(EXAMPLES["D1"][0]), False)
        self.assertEqual(got["note"], NO_AGENT_NOTE)
        self.assertIn("no agent work visible in this chat", got["note"])

    def test_the_same_scores_with_an_agent_are_orchestrator(self):
        self.assertEqual(overall(list(EXAMPLES["D1"][0]), True)["title"], "Orchestrator")

    def test_a_plain_delegator_has_no_note(self):
        self.assertIsNone(overall(list(EXAMPLES["D2"][0]), False)["note"])

    def test_three_at_three_without_delegation_is_practitioner(self):
        self.assertEqual(overall([3, 3, 3, 2, 2])["title"], "Practitioner")

    def test_three_at_four_with_delegation_at_three_is_delegator(self):
        got = overall([4, 4, 4, 3, 1], True)
        self.assertEqual((got["title"], got["note"]), ("Delegator", None))

    def test_delegation_not_shown_stops_at_practitioner(self):
        self.assertEqual(overall([5, 5, 5, NS, 5], True)["title"], "Practitioner")

    def test_multiplier_is_never_given(self):
        self.assertEqual(overall([5] * 5, True)["level"], 4)
        self.assertIn("Multiplier", overall([5] * 5, True)["note"])

    def test_a_mapping_finds_delegation_by_name_in_any_order(self):
        self.assertEqual(overall({"strategic_thinking": 3, "delegation": 2, "verification": 3,
                                  "workflow_design": 3, "problem_solving": 3})["title"], "Practitioner")
        self.assertEqual(overall({"Delegation": 3, "Verification": 3, "Workflow Design": 3,
                                  "Problem Solving": 1, "Strategic Thinking": 1})["title"], "Delegator")

    def test_lines(self):
        self.assertEqual(overall(list(EXAMPLES["D2"][0]))["line"],
                         "This chat: Delegator · Level 3 (at least 3 of 5 capabilities at Level 3 or higher, "
                         "including Delegation).")
        self.assertEqual(overall(list(EXAMPLES["D1"][0]))["line"],
                         "This chat: Delegator · Level 3 (at least 3 of 5 capabilities at Level 3 or higher, "
                         "including Delegation).")
        self.assertEqual(overall(list(EXAMPLES["O1"][0]), True)["line"],
                         "This chat: Orchestrator · Level 4 (at least 3 of 5 capabilities at Level 4 or higher, "
                         "including Delegation, with agent work shown).")
        self.assertEqual(overall(list(EXAMPLES["P1"][0]))["line"],
                         "This chat: Practitioner · Level 2 (at least 3 of 5 capabilities at Level 2 or higher).")
        self.assertEqual(overall(list(EXAMPLES["E1"][0]))["line"],
                         "This chat: Explorer · Level 1 (at least 3 of 5 capabilities shown).")
        self.assertEqual(overall([NS, 5, NS, NS, 3])["line"],
                         "This chat: No title yet (only 2 of 5 capabilities shown; a title needs at least 3).")
        self.assertEqual(overall([NS, 5, NS, NS, NS])["line"],
                         "This chat: No title yet (only 1 of 5 capabilities shown; a title needs at least 3).")


if __name__ == "__main__":
    unittest.main()
