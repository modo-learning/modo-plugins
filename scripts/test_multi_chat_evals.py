"""python3 -m unittest scripts/test_multi_chat_evals.py

Ticket 18: the eval cases for assess-my-chats, and the routing line in
assess-my-ai-work that points to it.
"""

import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "modo-ai-skills"
SINGLE = PLUGIN / "skills" / "assess-my-ai-work" / "SKILL.md"
MULTI = PLUGIN / "skills" / "assess-my-chats" / "SKILL.md"


def folded(path):
    """A skill with line breaks folded, so phrases match across wrapped lines."""
    return re.sub(r"[ \t]*\n[ \t]*(?=\S)(?![-#|`]|\d+\. )", " ", path.read_text())


class Routing(unittest.TestCase):
    def test_single_chat_skill_points_to_assess_my_chats_for_many_chats(self):
        body = folded(SINGLE)
        rule = body[body.index('If the user asks for "all my chats"'):]
        rule = rule[:rule.index("\n")]
        self.assertIn("/assess-my-chats", rule)
        self.assertIn("claude.ai", rule)
        self.assertIn("assess the current chat", rule)

    def test_one_chat_line_in_the_output_names_assess_my_chats(self):
        self.assertRegex(folded(SINGLE), r'one-chat line \("I assess one chat at a time, so this covers only '
                                         r'this chat\. [^"]*/assess-my-chats[^"]*"\)')


class CanItRun(unittest.TestCase):
    """Step 0 decides by the tools present, not by the app's name, so the
    eval's mocked chat tools (served as mcp__chats__recent_chats and so on)
    are found, and a run with no chat tools stops."""

    def step0(self):
        body = folded(MULTI)
        return body[body.index("## 0. Can this run here?"):body.index("## 1. Scope and list")]

    def test_decides_by_the_tools_present_under_any_prefix(self):
        step = self.step0()
        self.assertIn("by their names", step)
        self.assertIn("prefix", step)
        self.assertIn("tool search", step)

    def test_without_the_tools_it_stops_before_any_read(self):
        step = self.step0()
        self.assertIn("**Neither tool, in Claude Code or Cowork**", step)
        self.assertIn("**In claude.ai without those tools**", step)
        self.assertIn("Stop.", step)


if __name__ == "__main__":
    unittest.main()
