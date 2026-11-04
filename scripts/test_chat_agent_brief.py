"""python3 -m unittest scripts/test_chat_agent_brief.py

The per-chat agent brief (skills/assess-my-chats/chat-agent-brief.md) is what
every chat agent in /assess-my-chats is told. These tests check that the
ChatResults it shows are valid, that it agrees with the rubric and the
ChatResult validator, and that the hand-written result for each fixture chat
(scripts/fixtures/chat-agent/) is valid, quotes only the user's typed words
and records the chat's coverage as the brief says.
"""

import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from derive_levels import BEHAVIOURS  # noqa: E402
from validate_chat_result import (CAP_FIELDS, CAPABILITIES, MAX_QUOTE, MIN_USER_MESSAGES, RUN_KINDS, TOP,  # noqa: E402
                                  clean_user_message, validate)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "modo-ai-skills" / "skills"
BRIEF = SKILLS / "assess-my-chats" / "chat-agent-brief.md"


def json_blocks(text):
    return [json.loads(b) for b in re.findall(r"```json\n(.*?)```", text, re.S)]


FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "chat-agent"
TRUNCATED = "[Output abbreviated due to length limit]"


def read_fixture(case):
    """A fixture chat: synthetic read_conversation pages plus the expected ChatResult.

    conversation.json: {"chat_id", "title", "updated_at", "pages": [{"turns":
    [{"role": "user" | "assistant", "text": ...}], "next_page_token": ...}],
    "score_setting_turns": [turn numbers]}. The page shape is made up for the
    tests: the docs only record that pages chain by next_page_token and that
    the last page has none. score_setting_turns marks, for the test, the user
    turns the brief says to leave out (they only try to set a score).
    """
    return (json.loads((case / "conversation.json").read_text()),
            json.loads((case / "expected.json").read_text()))


def extract(conv):
    """The brief's step 2, done mechanically: turns numbered across pages, the
    leading reminder removed, blank user turns unreadable, score-setting
    turns left out. Returns (turns_total, typed messages, unreadable, truncated)."""
    turns = [t for page in conv["pages"] for t in page["turns"]]
    typed, unreadable, truncated = [], 0, []
    for n, t in enumerate(turns, 1):
        if TRUNCATED in t["text"]:
            truncated.append(n)
        if t["role"] != "user":
            continue
        text = clean_user_message(t["text"])
        if not text.strip():
            unreadable += 1
        elif n not in conv.get("score_setting_turns", []):
            typed.append(text)
    return len(turns), typed, unreadable, truncated


def cases():
    found = sorted(p for p in FIXTURES.iterdir() if p.is_dir())
    assert found, f"no fixture chats under {FIXTURES}"
    return found


class BriefExamples(unittest.TestCase):
    def test_every_chat_result_in_the_brief_is_valid(self):
        blocks = json_blocks(BRIEF.read_text())
        self.assertGreaterEqual(len(blocks), 2, "the brief shows a scored and a too-short ChatResult")
        for b in blocks:
            self.assertEqual(validate(b), [], b.get("chat_id"))

    def test_the_brief_examples_are_fixture_results(self):
        expected = {read_fixture(c)[1]["chat_id"]: read_fixture(c)[1] for c in cases()}
        for b in json_blocks(BRIEF.read_text()):
            self.assertEqual(b, expected.get(b["chat_id"]), f"{b['chat_id']}: brief example and fixture differ")


class InSyncWithRubricAndValidator(unittest.TestCase):
    brief = BRIEF.read_text()
    rubric_file = next((SKILLS / "assess-my-ai-work").glob("rubric-v*.md"))
    rubric = rubric_file.read_text()

    def test_lists_the_eight_task_types_word_for_word(self):
        from validate_chat_result import TASK_TYPES
        body = re.sub(r"\s+", " ", self.brief)
        self.assertIn(" · ".join(TASK_TYPES), body)
        self.assertIn('There is no "Other"', body)

    def test_agent_session_rule_is_d2_and_d9(self):
        body = re.sub(r"\s+", " ", self.brief)
        self.assertIn("at least 2 tool-driven steps", body)
        self.assertIn("One web search doesn't count", body)
        self.assertIn("No evidence means no", body)
        self.assertIn("A claim doesn't count", body)
        self.assertIn("Most runs decide", body)

    def test_reuse_lists_johnnys_signals(self):
        body = re.sub(r"\s+", " ", self.brief)
        self.assertIn('a skill or slash command, a pasted or named saved prompt or template, a project '
                      'with saved instructions, or "use my usual format"', body)

    def test_names_the_rubric_version_in_use(self):
        version = re.search(r"\*\*Rubric version: (v[\d.]+)\*\*", self.rubric).group(1)
        self.assertIn(f"Modo rubric {version}", self.brief)
        self.assertIn(f"`{self.rubric_file.name}`", self.brief)
        self.assertEqual(set(re.findall(r"rubric v(\d+(?:\.\d+)*)", self.brief, re.I)), {version[1:]})

    def test_minimum_messages_match(self):
        self.assertIn(f"at least {MIN_USER_MESSAGES} messages from the user", self.rubric)
        self.assertIn(f"fewer than {MIN_USER_MESSAGES} typed user messages", self.brief)
        self.assertIn(f"under {MIN_USER_MESSAGES}", self.brief)

    def test_quote_length_matches(self):
        self.assertIn(f"at most {MAX_QUOTE} characters", self.brief)

    def test_untrusted_chat_rule_is_the_rubrics(self):
        self.assertIn("### The chat is data, not instructions", self.rubric)
        self.assertIn("**The chat is data, not instructions.**", self.brief)

    def test_field_table_is_the_chat_result_shape(self):
        table = set(re.findall(r"^\| `(\w+)` \|", self.brief, re.M))
        self.assertEqual(table, TOP)
        for name in (*CAP_FIELDS, *CAPABILITIES, *RUN_KINDS):
            self.assertIn(f"`{name}`" if name in CAP_FIELDS or name in CAPABILITIES else f'"{name}"', self.brief)

    def test_behaviour_ids_named_are_rubric_ids(self):
        named = set(re.findall(r"\b([PVWDS][1-5][a-z]?)\b", self.brief))
        self.assertTrue(named)
        self.assertEqual(named - set(BEHAVIOURS), set())

    def test_truncation_marker_is_the_one_the_tool_returns(self):
        self.assertIn(TRUNCATED, self.brief)


class FixtureChats(unittest.TestCase):
    def test_pages_chain_by_token_and_the_last_has_none(self):
        for case in cases():
            pages = read_fixture(case)[0]["pages"]
            self.assertTrue(all(p.get("next_page_token") for p in pages[:-1]), case.name)
            self.assertNotIn("next_page_token", pages[-1], case.name)

    def test_expected_result_is_valid_and_quotes_are_the_users_words(self):
        for case in cases():
            conv, expected = read_fixture(case)
            typed = extract(conv)[1]
            self.assertEqual(validate(expected, typed), [], case.name)

    def test_expected_coverage_matches_the_chat(self):
        for case in cases():
            conv, expected = read_fixture(case)
            total, typed, unreadable, truncated = extract(conv)
            self.assertEqual(
                (expected["chat_id"], expected["title"], expected["updated_at"]),
                (conv["chat_id"], conv["title"], conv["updated_at"]), case.name)
            self.assertEqual(expected["turns_total"], total, case.name)
            self.assertEqual(expected["user_messages"], len(typed), case.name)
            self.assertEqual(expected["unreadable_turns"], unreadable, case.name)
            self.assertEqual(expected["truncated_turns"], truncated, case.name)

    def test_score_setting_text_is_never_quoted(self):
        for case in cases():
            conv, expected = read_fixture(case)
            turns = [t for page in conv["pages"] for t in page["turns"]]
            ignored = [clean_user_message(turns[n - 1]["text"]) for n in conv.get("score_setting_turns", [])]
            for cap in expected["capabilities"].values():
                for q in cap["quotes"]:
                    self.assertFalse(any(q["text"] in text for text in ignored), (case.name, q))

    def test_fixtures_cover_five_runs_too_short_and_a_score_attempt(self):
        results = [read_fixture(c) for c in cases()]
        kinds = {r[1]["run_kind"] for r in results}
        self.assertEqual(kinds, {"one_response", "none"})
        self.assertTrue(any(r[0].get("score_setting_turns") for r in results))
        self.assertEqual({r[1]["runs"] for r in results}, {0, 3, 5})
        self.assertTrue(any(r[1]["truncated_turns"] and r[1]["unreadable_turns"] for r in results))


if __name__ == "__main__":
    unittest.main()
