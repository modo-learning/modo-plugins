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
LABEL = "Self-assessment by Claude using Modo rubric v1 — not verified."

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


@unittest.skipUnless(CHROME, "no headless Chrome found")
class Render(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = render(SAMPLE)
        cls.items = items(cls.dom)

    def test_five_capabilities_in_rubric_order(self):
        self.assertEqual(
            [name_of(i) for i in self.items],
            ["Problem Solving", "Verification", "Workflow Design",
             "Delegation", "Strategic Thinking"],
        )

    def test_ring_values_are_band_midpoints(self):
        got = {}
        for i in self.items:
            v = re.search(r'data-value="(\d+)"', i)
            got[name_of(i)] = int(v.group(1)) if v else None
        self.assertEqual(got["Problem Solving"], 70)
        self.assertEqual(got["Verification"], 90)
        self.assertEqual(got["Workflow Design"], 30)
        self.assertEqual(got["Delegation"], 30)
        self.assertIsNone(got["Strategic Thinking"])

    def test_level_and_confidence_text(self):
        v = next(i for i in self.items if name_of(i) == "Verification")
        text = re.sub(r"<[^>]+>", " ", v)
        self.assertIn("Level 5 of 5", text)
        self.assertIn("high confidence", text.lower())

    def test_not_shown_is_not_a_zero(self):
        n = next(i for i in self.items if name_of(i) == "Strategic Thinking")
        text = re.sub(r"<[^>]+>", " ", n)
        self.assertIn("Not shown", text)
        self.assertIn("ring-empty", n)
        self.assertNotIn("data-value", n)
        self.assertNotIn("stroke-dashoffset", n)
        self.assertNotRegex(text, r"\b0\b")
        self.assertNotIn("Level", text)

    def test_label_verbatim_and_last(self):
        body = self.dom.split("<body", 1)[1]
        body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
        lines = [l.strip() for l in re.sub(r"<[^>]+>", "\n", body).splitlines() if l.strip()]
        self.assertEqual(lines[-1], LABEL)

    def test_evidence_shown_and_escaped(self):
        data = json.loads(json.dumps(SAMPLE))
        data["evidence"] = [{"capability": "Verification",
                             "quote": 'Check <b>this</b> & "that"'}]
        dom = render(data)
        self.assertIn("Check &lt;b&gt;this&lt;/b&gt; &amp;", dom)
        self.assertNotIn("<b>this</b>", dom)

    def test_no_verified_wording_outside_label(self):
        body = self.dom.split("<body", 1)[1]
        body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", body).replace(LABEL, "")
        self.assertNotRegex(text.lower(), r"verified|badge|benchmark|rank")

    def test_all_not_shown(self):
        data = json.loads(json.dumps(SAMPLE))
        for c in data["capabilities"]:
            c["level"] = "not_shown"
            c.pop("confidence", None)
        data["evidence"] = []
        its = items(render(data))
        self.assertEqual(len(its), 5)
        self.assertTrue(all("ring-empty" in i and "data-value" not in i for i in its))


if __name__ == "__main__":
    unittest.main()
