"""python3 -m unittest scripts/test_passport_card.py

Fills the passport card template with sample data the way the skill does
(replace the JSON between the two markers) and renders it in headless Chrome.
The render tests are skipped when no Chrome is found.
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "modo-ai-skills"
TEMPLATE = PLUGIN / "skills" / "assess-my-ai-work" / "passport-card.html"
HISTORY = PLUGIN / "evals" / "strong-verify-weak-delegate" / "history.jsonl"
LABEL = "Self-assessment by Claude using Modo rubric v1.1 — not verified."

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fill_passport_card import fill, MULTI_SAMPLE, SAMPLE  # noqa: E402

CHROME = next(
    filter(
        None,
        [
            shutil.which("google-chrome"),
            shutil.which("chromium"),
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ],
    ),
    None,
)
CHROME = CHROME if CHROME and pathlib.Path(CHROME).exists() else None


def render(data):
    html = fill(TEMPLATE.read_text(), data)
    with tempfile.TemporaryDirectory() as t:
        f = pathlib.Path(t) / "card.html"
        f.write_text(html)
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=2000", "--dump-dom", f.as_uri()],
            capture_output=True, text=True, timeout=60,
        )
    return out.stdout


def items(dom):
    return re.findall(r"<li[^>]*data-capability.*?</li>", dom, flags=re.S)


def name_of(item):
    return re.search(r'data-capability="([^"]+)"', item).group(1)


class Template(unittest.TestCase):
    def test_has_one_marked_data_block(self):
        text = TEMPLATE.read_text()
        self.assertEqual(text.count("MODO-DATA-START"), 1)
        self.assertEqual(text.count("MODO-DATA-END"), 1)

    def test_no_network_references(self):
        text = TEMPLATE.read_text()
        # the SVG namespace id is not a request
        self.assertNotRegex(text.replace("http://www.w3.org/2000/svg", ""), r"https?://")
        self.assertNotRegex(text, r"<link\b|<img\b|@import|fetch\(|XMLHttpRequest")

    def test_no_forbidden_wording(self):
        text = TEMPLATE.read_text().lower()
        for w in ("modo verified", "badge", "benchmark", "percentile", "rank"):
            self.assertNotIn(w, text)

    def test_sample_quotes_are_verbatim_user_messages(self):
        users = []
        for line in HISTORY.read_text().splitlines():
            m = json.loads(line)
            if m["type"] == "user":
                users.append(m["message"]["content"])
        for e in SAMPLE["evidence"]:
            self.assertLessEqual(len(e["quote"]), 240)
            self.assertTrue(any(e["quote"] in u for u in users), e["quote"])


def text_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def body_text(dom):
    body = dom.split("<body", 1)[1]
    return re.sub(r"<script.*?</script>", "", body, flags=re.S)


@unittest.skipUnless(CHROME, "no headless Chrome found")
class Render(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = render(SAMPLE)
        cls.items = items(cls.dom)

    def test_strengths_first_then_not_shown_last(self):
        # Sample levels: PS 4 medium, V 5 high, WD 2 low, D 2 medium, ST not shown.
        # Highest level first; a tie goes to the higher confidence.
        self.assertEqual(
            [name_of(i) for i in self.items],
            ["Verification", "Problem Solving", "Delegation", "Workflow Design",
             "Strategic Thinking"],
        )

    def test_headline_names_the_strongest(self):
        self.assertIn("Strongest in this chat: Verification", text_of(body_text(self.dom)))

    def test_segments_filled_to_the_level(self):
        got = {name_of(i): (i.count('class="seg on'), i.count('class="seg')) for i in self.items}
        self.assertEqual(got["Verification"], (5, 5))
        self.assertEqual(got["Problem Solving"], (4, 5))
        self.assertEqual(got["Workflow Design"], (2, 5))

    def test_confidence_and_agreement_visible(self):
        v = text_of(next(i for i in self.items if name_of(i) == "Verification"))
        self.assertIn("Level 5 of 5", v)
        self.assertIn("High confidence", v)
        self.assertIn("3 of 3 runs", v)
        w = next(i for i in self.items if name_of(i) == "Workflow Design")
        self.assertIn("Low confidence", text_of(w))
        self.assertIn('data-confidence="low"', w)

    def test_not_shown_is_a_dashed_empty_track(self):
        n = next(i for i in self.items if name_of(i) == "Strategic Thinking")
        text = text_of(n)
        self.assertIn("Not shown in this chat", text)
        self.assertIn("track-empty", n)
        self.assertNotIn('class="seg', n)
        self.assertNotIn("data-level", n)
        self.assertNotRegex(text, r"\b0\b")
        self.assertNotIn("Level", text)

    def test_session_count_and_coverage(self):
        text = text_of(body_text(self.dom))
        self.assertIn("Based on 1 chat", text)
        self.assertIn("This chat shows 4 of 5 capabilities. One more chat with different "
                      "work could show Strategic Thinking.", text)

    def test_growth_tip_and_next_action(self):
        text = text_of(body_text(self.dom))
        self.assertIn(SAMPLE["growth"]["tip"], text)
        self.assertIn(SAMPLE["next_action"], text)

    def test_label_verbatim_and_last(self):
        lines = [l.strip() for l in re.sub(r"<[^>]+>", "\n", body_text(self.dom)).splitlines() if l.strip()]
        self.assertEqual(lines[-1], LABEL)

    def test_evidence_shown_and_escaped(self):
        data = json.loads(json.dumps(SAMPLE))
        data["evidence"] = [{"capability": "Verification",
                             "quote": 'Check <b>this</b> & "that"'}]
        dom = render(data)
        self.assertIn("Check &lt;b&gt;this&lt;/b&gt; &amp;", dom)
        self.assertNotIn("<b>this</b>", dom)

    def test_no_verified_wording_outside_label(self):
        text = text_of(body_text(self.dom)).replace(LABEL, "")
        self.assertNotRegex(text.lower(), r"verified|badge|benchmark|rank")

    def test_runs_disagreed_is_not_missing_coverage(self):
        data = json.loads(json.dumps(SAMPLE))
        data["capabilities"][3] = {"name": "Delegation", "level": "not_shown", "agreement": "runs disagreed"}
        text = text_of(body_text(render(data)))
        self.assertIn("could show Strategic Thinking", text)
        self.assertNotIn("could show Delegation", text)
        self.assertIn("runs disagreed", text)

    def test_all_not_shown(self):
        data = json.loads(json.dumps(SAMPLE))
        for c in data["capabilities"]:
            c["level"] = "not_shown"
            c.pop("confidence", None)
        data["evidence"] = []
        dom = render(data)
        its = items(dom)
        self.assertEqual(len(its), 5)
        self.assertTrue(all("track-empty" in i and "data-level" not in i for i in its))
        text = text_of(body_text(dom))
        self.assertNotIn("Strongest", text)
        self.assertIn("This chat shows only 0 of 5 capabilities", text)


def overall_of(dom):
    """(data-overall, text) of the card's overall AI fluency line."""
    m = re.search(r'<p[^>]*id="fluency"[^>]*>.*?</p>', dom, flags=re.S)
    return re.search(r'data-overall="([^"]+)"', m.group(0)).group(1), text_of(m.group(0))


@unittest.skipUnless(CHROME, "no headless Chrome found")
class RenderOverall(unittest.TestCase):
    """The overall AI fluency title, worked out in the card from the five levels
    (decided 2026-11-03, flag for review: Angelina, Johnny)."""

    def with_levels(self, levels, base=SAMPLE):
        data = json.loads(json.dumps(base))
        for c, lvl in zip(data["capabilities"], levels):
            c["level"] = lvl
            if lvl == "not_shown":
                c.pop("confidence", None)
            else:
                c.setdefault("confidence", "medium")
        return render(data)

    def test_sample_is_practitioner(self):
        # Sample levels 4, 5, 2, 2, not shown: four at 2 or higher, two at 3 or higher.
        level, text = overall_of(render(SAMPLE))
        self.assertEqual(level, "2")
        self.assertIn("Practitioner \u00b7 Level 2", text)
        self.assertIn("at least 3 of 5 capabilities at Level 2 or higher", text)

    def test_level_5_everywhere_is_capped_at_orchestrator(self):
        level, text = overall_of(self.with_levels([5, 5, 5, 5, 5]))
        self.assertEqual(level, "4")
        self.assertIn("Orchestrator \u00b7 Level 4", text)
        self.assertNotIn("Multiplier", text)

    def test_fewer_than_3_shown_is_not_enough(self):
        level, text = overall_of(self.with_levels([2, "not_shown", "not_shown", "not_shown", 1]))
        self.assertEqual(level, "none")
        self.assertIn("Overall: not enough shown", text)
        self.assertNotRegex(text, r"Explorer|Practitioner|Delegator|Orchestrator")

    def test_multi_chat_uses_the_combined_levels(self):
        # Combined levels 2, 3, 2, 3, not shown.
        level, text = overall_of(render(MULTI_SAMPLE))
        self.assertEqual(level, "2")
        self.assertIn("Practitioner \u00b7 Level 2", text)

    def test_the_card_and_the_python_rule_agree_on_the_worked_examples(self):
        from test_derive_levels import OVERALL_WORKED
        from derive_levels import overall
        for levels, _ in OVERALL_WORKED:
            with self.subTest(levels=levels):
                data = json.loads(json.dumps(SAMPLE))
                for c, lvl in zip(data["capabilities"], levels):
                    if isinstance(lvl, int):
                        c.update(level=lvl, confidence="medium", agreement="3 of 3 runs")
                    else:
                        c.pop("confidence", None)
                        c.update(level="not_shown",
                                 agreement="runs disagreed" if lvl == "runs disagreed" else "3 of 3 runs")
                want = overall(levels)["level"]
                self.assertEqual(overall_of(render(data))[0], "none" if want is None else str(want))


@unittest.skipUnless(CHROME, "no headless Chrome found")
class RenderMultiChat(unittest.TestCase):
    """A result across several chats (assess-my-chats). Proposal: card look is Angelina's."""

    @classmethod
    def setUpClass(cls):
        cls.dom = render(MULTI_SAMPLE)
        cls.items = items(cls.dom)
        cls.text = text_of(body_text(cls.dom))

    def item(self, name):
        return next(i for i in self.items if name_of(i) == name)

    def test_header_names_the_chat_count_and_date_range(self):
        self.assertIn("Based on 4 chats, 2026-10-06 to 2026-10-30, against Modo rubric v1.1.", self.text)
        self.assertIn("Strongest across these chats: Verification", self.text)
        self.assertNotIn("this chat", self.text.lower())

    def test_order_strengths_first(self):
        # Sample: P 2 high, V 3 high, W 2 medium, D 3 medium, S not shown.
        self.assertEqual([name_of(i) for i in self.items],
                         ["Verification", "Delegation", "Problem Solving", "Workflow Design",
                          "Strategic Thinking"])

    def test_trend_arrow_per_capability(self):
        v = self.item("Verification")
        self.assertIn('data-trend="up"', v)
        self.assertIn('aria-label="Trend: up"', v)
        self.assertIn("\u2191", v)
        self.assertNotIn("data-trend", self.item("Delegation"))

    def test_down_and_flat_arrows(self):
        data = json.loads(json.dumps(MULTI_SAMPLE))
        data["capabilities"][0]["trend"] = "down"
        data["capabilities"][1]["trend"] = "flat"
        its = items(render(data))
        p = next(i for i in its if name_of(i) == "Problem Solving")
        v = next(i for i in its if name_of(i) == "Verification")
        self.assertIn("\u2193", p)
        self.assertIn('aria-label="Trend: down"', p)
        self.assertIn("\u2192", v)
        self.assertIn('aria-label="Trend: flat"', v)

    def test_chats_shown_and_best_shown(self):
        v = text_of(self.item("Verification"))
        self.assertIn("Level 3 of 5", v)
        self.assertIn("High confidence", v)
        self.assertIn("Shown in 4 of 4 chats", v)
        self.assertIn("Best shown: Level 4", v)
        self.assertNotIn("Best shown", text_of(self.item("Delegation")))

    def test_not_shown_in_these_chats(self):
        s = self.item("Strategic Thinking")
        self.assertIn("Not shown in these chats", text_of(s))
        self.assertIn("track-empty", s)
        self.assertNotIn("data-trend", s)

    def test_coverage_line_for_several_chats(self):
        self.assertIn("These chats show 4 of 5 capabilities. A chat with different work "
                      "could show Strategic Thinking.", self.text)

    def test_partial_coverage(self):
        data = json.loads(json.dumps(MULTI_SAMPLE))
        for c in data["capabilities"][2:]:
            c.update(level="not_shown", trend=None, best_shown=None, chats_shown=0)
            c.pop("confidence", None)
        self.assertIn("These chats show only 2 of 5 capabilities, so this is a partial picture.",
                      text_of(body_text(render(data))))

    def test_evidence_names_its_chat(self):
        self.assertIn(MULTI_SAMPLE["evidence"][0]["quote"], self.text)
        self.assertIn("Verification · Chat 4, 2026-10-14", self.text)

    def test_label_verbatim_and_last(self):
        lines = [l.strip() for l in re.sub(r"<[^>]+>", "\n", body_text(self.dom)).splitlines() if l.strip()]
        self.assertEqual(lines[-1], LABEL)
        self.assertNotRegex(self.text.replace(LABEL, "").lower(), r"verified|badge|benchmark|rank")

    def test_nothing_shown_across_chats(self):
        data = json.loads(json.dumps(MULTI_SAMPLE))
        for c in data["capabilities"]:
            c.update(level="not_shown", trend=None, best_shown=None, chats_shown=0)
            c.pop("confidence", None)
        data["evidence"] = []
        text = text_of(body_text(render(data)))
        self.assertIn("Your AI capabilities across these chats", text)
        self.assertNotIn("this chat", text)

    def test_headline_names_every_capability_tied_at_the_top(self):
        # Live test 2026-11-02, defect 4: Problem Solving and Delegation both level 4.
        data = json.loads(json.dumps(MULTI_SAMPLE))
        for c in data["capabilities"]:
            if c["name"] in ("Problem Solving", "Delegation"):
                c.update(level=4, confidence="medium")
        text = text_of(body_text(render(data)))
        self.assertIn("Strongest across these chats: Problem Solving and Delegation", text)

    def test_headline_names_several_tied_in_rubric_order(self):
        data = json.loads(json.dumps(MULTI_SAMPLE))
        for c in data["capabilities"][:4]:
            c.update(level=3, confidence="high")
        text = text_of(body_text(render(data)))
        self.assertIn("Strongest across these chats: Problem Solving, Verification, Workflow Design and Delegation",
                      text)

    def test_a_tie_on_level_but_not_confidence_names_one(self):
        data = json.loads(json.dumps(MULTI_SAMPLE))
        data["capabilities"][3].update(level=3, confidence="medium")   # V is 3 high
        text = text_of(body_text(render(data)))
        self.assertIn("Strongest across these chats: Verification", text)
        self.assertNotIn("Verification and", text)

    def test_single_chat_card_has_no_trend(self):
        self.assertFalse([i for i in items(render(SAMPLE)) if "data-trend" in i])


if __name__ == "__main__":
    unittest.main()
