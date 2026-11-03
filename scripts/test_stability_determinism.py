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


def js_rule(html):
    """The overall loop from a template: `for (var L = 1; L <= 4; L++) { ... }`."""
    m = re.search(r"for \(var L = 1; L <= 4; L\+\+\) \{.*?\n\s*\}", html, re.S)
    if not m:
        raise AssertionError("no overall loop found")
    return m.group(0)


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

    def test_title_does_not_depend_on_capability_order(self):
        for levels in ALL[::7]:
            self.assertEqual(overall(levels), overall(list(reversed(levels))))


@unittest.skipUnless(NODE, "node not found")
class PythonAndJsAgree(unittest.TestCase):
    def test_every_template_gives_the_python_title_for_every_level_set(self):
        want = [overall([v if isinstance(v, int) else "not shown" for v in c])["level"] or 0 for c in ALL]
        self.assertTrue(TEMPLATES)
        for t in TEMPLATES:
            with self.subTest(template=str(t.relative_to(ROOT))):
                script = ("const ALL = %s; function shown(c) { return [1,2,3,4,5].indexOf(c.level) >= 0; }\n"
                          "console.log(JSON.stringify(ALL.map(function (levels) {\n"
                          "  var ordered = levels.map(function (v) { return {level: v}; });\n"
                          "  var overall = 0;\n  %s\n  return overall; })));" % (json.dumps(ALL), js_rule(t.read_text())))
                out = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=60)
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertEqual(json.loads(out.stdout), want)


if __name__ == "__main__":
    unittest.main()
