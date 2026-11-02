"""python3 -m unittest scripts/test_check_design_sync.py"""

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_design_sync import check  # noqa: E402

TOKENS = "/* MODO-TOKENS-START */\n:root { --x: #000; }\n/* MODO-TOKENS-END */\n"


def make(tmp, source=TOKENS, templates=(TOKENS,)):
    root = pathlib.Path(tmp)
    d = root / "skills" / "modo-design"
    d.mkdir(parents=True)
    (d / "modo-tokens.css").write_text(source)
    for i, body in enumerate(templates):
        s = root / "skills" / f"skill-{i}"
        s.mkdir()
        (s / "page.html").write_text(f"<style>\n{body}</style>\n")
    return root


class DesignSync(unittest.TestCase):
    def test_identical_copies_pass(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(check(make(t, templates=(TOKENS, TOKENS))), [])

    def test_diverged_copy_fails(self):
        with tempfile.TemporaryDirectory() as t:
            other = TOKENS.replace("#000", "#111")
            self.assertEqual(len(check(make(t, templates=(TOKENS, other)))), 1)

    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(check(pathlib.Path(t)))

    def test_no_template_fails(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(check(make(t, templates=())))

    def test_real_plugin_in_sync(self):
        root = pathlib.Path(__file__).parent.parent / "plugins" / "modo-ai-skills"
        self.assertEqual(check(root), [])

    def test_card_and_report_both_carry_tokens(self):
        root = pathlib.Path(__file__).parent.parent / "plugins" / "modo-ai-skills" / "skills"
        for t in ("assess-my-ai-work/passport-card.html", "export-assessment/report-template.html"):
            self.assertIn("MODO-TOKENS-START", (root / t).read_text(), t)


if __name__ == "__main__":
    unittest.main()
