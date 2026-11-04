"""python3 -m unittest scripts/test_stability_determinism.py (ticket 33).

Everything after the model finds behaviours is fixed code, so the same input
must always give the same output: the level rule, the combining of runs and
chats, and the overall title. The title is worked out in three places (Python,
the card's JS and the report's JS); for every one of the 6^5 possible sets of
five levels they must agree. The JS checks need node and are skipped without it.
"""

import itertools
import json
import pathlib
import random
import re
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from derive_levels import BEHAVIOURS, combine, derive, overall  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = sorted(ROOT.glob("**/skills/*/passport-card.html")) + sorted(ROOT.glob("**/skills/*/report-template.html"))
VALUES = [1, 2, 3, 4, 5, "not_shown"]
ALL = [list(c) for c in itertools.product(VALUES, repeat=5)]
NODE = shutil.which("node")


def block(html, name):
    """A marked block of a template's script; "" when it has none."""
    m = re.search(rf"/\* MODO-{name}-START \*/.*?/\* MODO-{name}-END \*/", html, re.S)
    return m.group(0) if m else ""


class SameInputSameOutput(unittest.TestCase):
    def test_level_rule_and_combine_are_repeatable_on_random_runs(self):
        rnd = random.Random(33)
        ids = sorted(BEHAVIOURS)
        for _ in range(500):
            letter = rnd.choice("PVWDS")
            pool = [b for b in ids if b.startswith(letter)]
            runs = [[(rnd.randint(1, 7), rnd.choice(pool)) for _ in range(rnd.randint(0, 5))] for _ in range(5)]
            first = combine([derive(r, 7) for r in runs])
            self.assertEqual(first, combine([derive(list(r), 7) for r in runs]))

    def test_combining_chats_does_not_depend_on_their_order(self):
        import aggregate_chats
        rnd = random.Random(34)
        keys = ("problem_solving", "verification", "workflow_design", "delegation", "strategic_thinking")
        for _ in range(300):
            chats = [(f"2026-10-{d:02d}", {k: rnd.choice([1, 2, 3, 4, 5, "not_shown"]) for k in keys})
                     for d in rnd.sample(range(1, 29), rnd.randint(1, 8))]
            shuffled = chats[:]
            rnd.shuffle(shuffled)
            self.assertEqual(aggregate_chats.combine(chats), aggregate_chats.combine(shuffled))

    def test_title_does_not_depend_on_the_order_of_the_other_capabilities(self):
        for levels in ALL[::7]:
            others = levels[:3] + levels[4:]
            shuffled = others[::-1]
            self.assertEqual(overall(levels, True), overall(shuffled[:3] + [levels[3]] + shuffled[3:], True))

    def test_person_title_does_not_depend_on_chat_order(self):
        import aggregate_chats
        rnd = random.Random(35)
        for _ in range(300):
            chats = [rnd.choice([None, 1, 2, 3, 4]) for _ in range(rnd.randint(0, 25))]
            shuffled = chats[:]
            rnd.shuffle(shuffled)
            self.assertEqual(aggregate_chats.person_title(chats), aggregate_chats.person_title(shuffled))


@unittest.skipUnless(NODE, "node not found")
class PythonAndJsAgree(unittest.TestCase):
    def run_js(self, source):
        out = subprocess.run([NODE, "-e", source], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def test_every_template_gives_the_python_title_for_every_level_set(self):
        self.assertTrue(TEMPLATES)
        for agent in (False, True):
            want = [overall([v if isinstance(v, int) else "not shown" for v in c], agent)["level"] or 0 for c in ALL]
            for t in TEMPLATES:
                with self.subTest(template=str(t.relative_to(ROOT)), agent=agent):
                    rule = block(t.read_text(), "RULE")
                    self.assertTrue(rule)
                    got = self.run_js("const ALL = %s;\n%s\nconsole.log(JSON.stringify(ALL.map(function (levels) {\n"
                                      "  return chatTitle(levels, levels[3], %s); })));"
                                      % (json.dumps(ALL), rule, json.dumps(agent)))
                    self.assertEqual(got, want)

    def test_the_rule_blocks_are_the_same_text_in_card_and_report(self):
        sources = [t for t in TEMPLATES if t.is_relative_to(ROOT / "plugins")]
        self.assertGreaterEqual(len(sources), 3)
        for name in ("RULE", "PERSON"):
            self.assertEqual(len({block(t.read_text(), name) for t in sources}), 1, name)

    def test_templates_agree_with_python_on_person_title_and_proven_level(self):
        import aggregate_chats as a
        rnd = random.Random(36)
        sheets = [[rnd.choice([1, 2, 3, 4]) for _ in range(rnd.randint(0, 25))] for _ in range(500)]
        titles = [a.reached_in(s) or 0 for s in sheets]
        for t in TEMPLATES:
            person = block(t.read_text(), "PERSON")
            if not person:
                continue
            with self.subTest(template=str(t.relative_to(ROOT))):
                got = self.run_js("const S = %s;\nvar LADDER = [];\n%s\nconsole.log(JSON.stringify(S.map(reachedIn)));"
                                  % (json.dumps(sheets), person))
                self.assertEqual(got, titles)

    def test_johnnys_examples_in_every_template(self):
        from test_johnny_rules import EDGE, EXAMPLES
        cases = [v for v in {**EXAMPLES, **EDGE}.values()]
        want = [c[3] or 0 for c in cases]
        for t in TEMPLATES:
            with self.subTest(template=str(t.relative_to(ROOT))):
                got = self.run_js("const C = %s;\n%s\nconsole.log(JSON.stringify(C.map(function (c) {\n"
                                  "  return chatTitle(c[0], c[0][3], c[1]); })));"
                                  % (json.dumps([[list(c[0]), c[1]] for c in cases]), block(t.read_text(), "RULE")))
                self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
