"""python3 -m unittest scripts/test_report_template.py

Fills the PDF report template with a record the way the export skill does
(replace the JSON between the two markers) and renders it in headless Chrome.
The render tests are skipped when no Chrome is found.
"""

import copy
import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fill_passport_card import fill, fill_summary  # noqa: E402
from test_passport_card import CHROME, text_of  # noqa: E402
from test_validate_assessment_record import MULTI  # noqa: E402
from validate_assessment_record import validate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "plugins" / "modo-ai-skills" / "skills" / "export-assessment" / "report-template.html"
LABEL = "Self-assessment by Claude using Modo rubric v1.1 — not verified."

RECORD = {
    "rubric_version": "v1.1",
    "capabilities": {
        "problem_solving": {"level": 4, "confidence": "medium"},
        "verification": {"level": 5, "confidence": "high"},
        "workflow_design": {"level": 3, "confidence": "medium"},
        "delegation": {"level": 3, "confidence": "medium"},
        "strategic_thinking": {"level": "not_shown", "confidence": "low"},
    },
    "evidence": [{"capability": "verification",
                  "quote": "I'll check the three results against my own spreadsheet before they go in the deck."}],
    "session_title": "Q3 pricing analysis and board deck",
    "session_date": "2026-10-29",
}


def render(record, summary=None):
    import subprocess
    import tempfile
    html = fill(TEMPLATE.read_text(), record)
    if summary is not None:
        html = fill_summary(html, summary)
    with tempfile.TemporaryDirectory() as t:
        f = pathlib.Path(t) / "report.html"
        f.write_text(html)
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=2000", "--dump-dom", f.as_uri()],
            capture_output=True, text=True, timeout=60,
        )
    return out.stdout


class Template(unittest.TestCase):
    def test_has_one_marked_data_block(self):
        text = TEMPLATE.read_text()
        self.assertEqual(text.count("MODO-DATA-START"), 1)
        self.assertEqual(text.count("MODO-DATA-END"), 1)

    def test_no_network_references(self):
        text = TEMPLATE.read_text()
        self.assertNotRegex(text, r"https?://")
        self.assertNotRegex(text, r"<link\b|<img\b|@import|fetch\(|XMLHttpRequest")

    def test_no_forbidden_wording(self):
        text = TEMPLATE.read_text().lower()
        for w in ("modo verified", "badge", "benchmark", "percentile", "rank"):
            self.assertNotIn(w, text)


@unittest.skipUnless(CHROME, "no Chrome found")
class Rendered(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = render(RECORD)
        cls.text = text_of(cls.dom)

    def test_title_and_date_line(self):
        self.assertIn("Modo AI Skills assessment: Q3 pricing analysis and board deck", self.text)
        self.assertIn("Chat date: 2026-10-29. Rubric: v1.1. Based on 1 chat.", self.text)
        self.assertIn(LABEL, self.text)

    def test_rows_in_rubric_order(self):
        keys = re.findall(r'<tr data-capability="([a-z_]+)"', self.dom)
        self.assertEqual(keys, list(RECORD["capabilities"]))

    def test_levels_and_not_shown_note(self):
        self.assertIn("5 of 5", self.text)
        self.assertIn("Not shown", self.text)
        self.assertIn('the record gives confidence "low"', self.text)

    def test_record_block_is_last_and_matches(self):
        block = re.search(r'<pre id="record">(.*?)</pre>', self.dom, re.S).group(1)
        self.assertEqual(json.loads(block.replace("&quot;", '"').replace("&amp;", "&")
                                    .replace("&lt;", "<").replace("&gt;", ">")), RECORD)
        main = re.search(r"<main.*?</main>", self.dom, re.S).group(0)
        self.assertTrue(re.sub(r"\s+", "", main).endswith("</pre></div></main>"))

    def test_scores_only(self):
        rec = copy.deepcopy(RECORD)
        rec["evidence"] = []
        self.assertIn("None. This export has scores only.", text_of(render(rec)))

    def test_quote_is_escaped(self):
        rec = copy.deepcopy(RECORD)
        rec["evidence"] = [{"capability": "verification", "quote": "<script>alert(1)</script> check"}]
        dom = render(rec)
        self.assertNotIn("<script>alert(1)</script>", dom.split("<!-- MODO-DATA-END -->")[0])


def overall_of(dom):
    """(data-overall, text) of the report's overall AI fluency line."""
    m = re.search(r'<p[^>]*id="fluency"[^>]*>.*?</p>', dom, re.S)
    return re.search(r'data-overall="([^"]+)"', m.group(0)).group(1), text_of(m.group(0))


def with_levels(levels):
    rec = copy.deepcopy(RECORD)
    for (key, c), lvl in zip(rec["capabilities"].items(), levels):
        c["level"] = lvl if isinstance(lvl, int) else "not_shown"
        c["confidence"] = "medium" if isinstance(lvl, int) else "low"
    rec["evidence"] = [e for e in rec["evidence"] if rec["capabilities"][e["capability"]]["level"] != "not_shown"]
    return rec


@unittest.skipUnless(CHROME, "no Chrome found")
class RenderedOverall(unittest.TestCase):
    """The title, worked out in the report from the capability levels and the agent
    session (Johnny's scoring rules v1, 2026-11-04). The record is unchanged."""

    def test_single_chat_record_is_delegator(self):
        # Levels 4, 5, 3, 3, not shown: four at 3 or higher, including Delegation.
        dom = render(RECORD)
        level, text = overall_of(dom)
        self.assertEqual(level, "3")
        self.assertIn("This chat: Delegator \u00b7 Level 3", text)
        self.assertIn("least 3 of 5 capabilities at Level 3 or higher, including Delegation", text)
        self.assertIn("The title is not part of the record.", text_of(dom))

    def test_orchestrator_needs_the_agent_session_from_the_summary(self):
        rec = with_levels([5, 5, 5, 5, 5])
        self.assertEqual(overall_of(render(rec, {"agent_session": True}))[0], "4")
        level, text = overall_of(render(rec, {"agent_session": False}))
        self.assertEqual(level, "3")
        self.assertIn("no agent work visible in this chat", text)

    def test_no_title_yet(self):
        level, text = overall_of(render(with_levels([2, "not_shown", "not_shown", "not_shown", 1])))
        self.assertEqual(level, "none")
        self.assertIn("This chat: No title yet", text)

    def test_the_record_block_has_no_title_and_no_summary_field(self):
        block = re.search(r'<pre id="record">(.*?)</pre>', render(RECORD, {"agent_session": True}), re.S).group(1)
        self.assertNotIn("overall", block.lower())
        self.assertNotIn("Delegator", block)
        self.assertNotIn("agent_session", block)

    def test_the_report_and_the_python_rule_agree_on_johnnys_examples(self):
        from test_johnny_rules import EDGE, EXAMPLES
        from derive_levels import overall
        for name, (levels, agent, _, _) in {**EXAMPLES, **EDGE}.items():
            with self.subTest(name):
                rec = with_levels(list(levels))
                self.assertEqual(validate(rec), [])
                want = overall(list(levels), agent)
                got, text = overall_of(render(rec, {"agent_session": agent}))
                self.assertEqual(got, "none" if want["level"] is None else str(want["level"]))
                self.assertIn(want["title"] or "No title yet", text)


@unittest.skipUnless(CHROME, "no Chrome found")
class RenderedMultiChat(unittest.TestCase):
    """A multi-chat record (RECORD.md "Multi-chat record"). Proposal: look is Angelina's."""

    @classmethod
    def setUpClass(cls):
        assert validate(MULTI) == []
        cls.dom = render(MULTI, {"chat_titles": [2, 3, None, 2, 2], "task_types": 3, "reused": 1})
        cls.text = text_of(cls.dom)

    def test_title_and_chats_line(self):
        self.assertIn("Modo AI Skills assessment: Assessment across 4 chats", self.text)
        date_line = re.search(r'<p class="sub" id="date">(.*?)</p>', self.dom).group(1)
        self.assertEqual(date_line, "Chats: 2026-10-06 to 2026-10-30. Rubric: v1.1. Based on 4 chats.")

    def test_multi_chat_notes_replace_the_single_chat_notes(self):
        self.assertRegex(self.dom, r'<p id="notes-single" hidden="">')
        self.assertRegex(self.dom, r'<p id="notes-multi">Levels run from 1 to 5. Each level combines')
        note = re.search(r'<p id="ns-note">(.*?)</p>', self.dom).group(1)
        self.assertIn("no scored chat supports a level", note)
        self.assertIn(LABEL, self.text)

    def test_under_10_chats_shows_the_count_and_the_signals(self):
        level, text = overall_of(self.dom)
        self.assertEqual(level, "pending")
        self.assertIn("4 of 10 chats to your title", text)
        self.assertIn("Task range: 3 of 8 types", text)
        self.assertIn("Reused saved work: 1 of 4 chats", text)

    def test_ten_scored_chats_show_the_title(self):
        rec = copy.deepcopy(MULTI)
        rec["chats_assessed"]["scored"] = 10
        level, text = overall_of(render(rec, {"chat_titles": [3, 3, 3] + [1] * 7}))
        self.assertEqual(level, "3")
        self.assertIn("Your title: Delegator \u00b7 Level 3", text)

    def test_capability_rows_show_proven_trend_and_chats_shown(self):
        rows = dict(re.findall(r'<tr data-capability="([a-z_]+)"[^>]*>(.*?)</tr>', self.dom, re.S))
        self.assertEqual(list(rows), list(MULTI["capabilities"]))
        v = text_of(rows["verification"])
        # Verification 4, 4, 3, 3: Level 3 reached in 4 chats, Level 4 in 2. best_shown is 4 in the record.
        for part in ("3 of 5", "high", "Level 3", "\u2191 up", "4 of 4"):
            self.assertIn(part, v)
        self.assertNotIn("Level 4", v)
        self.assertRegex(self.dom, r"<th>Proven level</th>")
        self.assertNotIn("<th>Best shown</th>", self.dom)
        d = text_of(rows["delegation"])
        self.assertIn("3 of 4", d)
        self.assertNotIn("\u2191", d)
        s = text_of(rows["strategic_thinking"])
        self.assertIn("Not shown", s)
        self.assertIn("0 of 4", s)

    def test_per_chat_table(self):
        rows = re.findall(r'<tr data-chat="(\d+)"[^>]*>(.*?)</tr>', self.dom, re.S)
        self.assertEqual([n for n, _ in rows], ["1", "2", "3", "4", "5"])
        first = text_of(rows[0][1])
        self.assertIn("Chat 1", first)
        self.assertIn("2026-10-30", first)
        self.assertIn("scored", first)
        self.assertIn("too short", text_of(rows[2][1]))
        self.assertIn("Practitioner", first)
        self.assertIn("Delegator", text_of(rows[1][1]))
        self.assertEqual(re.findall(r"<td[^>]*>([^<]*)</td>", rows[3][1])[-5:], ["2", "3", "2", "3", "\u2013"])

    def test_evidence_names_its_chat(self):
        self.assertIn("Verification \u00b7 Chat 4, 2026-10-14", self.text)

    def test_the_record_block_stays_the_record(self):
        block = re.search(r'<pre id="record">(.*?)</pre>', self.dom, re.S).group(1)
        self.assertIn("best_shown", block)
        for word in ("proven", "chat_titles", "task_types", "reused"):
            self.assertNotIn(word, block)

    def test_record_block_is_last_and_matches(self):
        block = re.search(r'<pre id="record">(.*?)</pre>', self.dom, re.S).group(1)
        self.assertEqual(json.loads(block.replace("&quot;", '"').replace("&amp;", "&")
                                    .replace("&lt;", "<").replace("&gt;", ">")), MULTI)
        main = re.search(r"<main.*?</main>", self.dom, re.S).group(0)
        self.assertTrue(re.sub(r"\s+", "", main).endswith("</pre></div></main>"))

    def test_single_chat_report_has_no_chats_table(self):
        dom = render(RECORD)
        self.assertNotIn('data-chat="', dom.split("<!-- MODO-DATA-END -->")[0])
        self.assertIn("Based on 1 chat.", text_of(dom))


if __name__ == "__main__":
    unittest.main()
