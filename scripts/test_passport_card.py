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
from fill_passport_card import fill, SAMPLE  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
