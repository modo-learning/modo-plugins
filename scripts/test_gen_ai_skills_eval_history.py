"""python3 -m unittest scripts/test_gen_ai_skills_eval_history.py

The save cases' mocks of the Modo connector (ticket 10)."""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import gen_ai_skills_eval_history as gen  # noqa: E402

EVALS = pathlib.Path(__file__).resolve().parent.parent / "plugins" / "modo-ai-skills" / "evals"

# modo-mcp's answer when its store fails (modo-mcp, ticket 09: save_assessment
# handler; copied by hand, not from the generator).
STORE_FAILURE = "save_assessment failed: the assessment could not be stored. Nothing was saved; try again later."


class GradersAndCases(unittest.TestCase):
    def test_graders_name_the_current_rubric_only(self):
        for path in EVALS.glob("*/graders/*.md"):
            with self.subTest(path=str(path)):
                self.assertNotRegex(path.read_text(), r"v1(?:\\)?\.1\b")


class SaveMock(unittest.TestCase):
    def test_guards_every_expected_quote_and_no_more(self):
        mock = gen.save_mock(4)
        self.assertIn("evidence.3.quote:", mock)
        self.assertNotIn("evidence.4.quote:", mock)

    def test_no_quote_guards_when_no_save_is_expected(self):
        self.assertNotIn("evidence.0.quote:", gen.save_mock(None))

    def test_rejection_is_the_real_store_failure(self):
        mock = gen.save_mock(5, error=True)
        self.assertIn("error: true\n", mock)
        self.assertTrue(mock.endswith("---\n" + STORE_FAILURE + "\n"))


class CommittedMocks(unittest.TestCase):
    def test_committed_save_mocks_match_the_generator(self):
        for case in gen.CONNECTOR_CASES:
            with self.subTest(case=case):
                path = EVALS / case / "mocks" / "modo" / f"{gen.SAVE_TOOL}.md"
                self.assertEqual(path.read_text(), gen.case_save_mock(case))

    def test_committed_passport_mocks_match_the_generator(self):
        for case in gen.CONNECTOR_CASES:
            with self.subTest(case=case):
                path = EVALS / case / "mocks" / "modo" / f"{gen.PASSPORT_TOOL}.md"
                self.assertEqual(path.read_text(), gen.case_passport_mock(case))

    def test_passport_shown_returns_the_save_its_history_recorded(self):
        # The id and date the recorded save returned (passport-shown/history.jsonl).
        passport = json.loads(gen.case_passport_mock("passport-shown"))
        self.assertEqual([(h["id"], h["session_date"]) for h in passport["history"]],
                         [("2fda9db3-a075-4476-ab50-e6d89bf9ee4a", "2026-10-27")])
        self.assertEqual(passport["latest"]["verification"]["level"], 5)

    def test_only_connector_cases_have_the_connector(self):
        with_mocks = sorted(p.parent.parent.name for p in EVALS.glob("*/mocks/modo"))
        self.assertEqual(with_mocks, sorted(gen.CONNECTOR_CASES))


if __name__ == "__main__":
    unittest.main()
