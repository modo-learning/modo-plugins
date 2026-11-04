"""python3 -m unittest scripts/test_stability_report.py (ticket 33)."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import stability_report as sr  # noqa: E402

# Krippendorff, K. (2011). Computing Krippendorff's Alpha-Reliability.
# Annenberg School for Communication, University of Pennsylvania, section D
# ("Ordinal Metric", worked example): 4 observers, 12 units, values 1-5,
# None = missing. Published results: nominal .743, ordinal .815, interval .849.
K2011 = [
    [1, 1, None, 1], [2, 2, 3, 2], [3, 3, 3, 3], [3, 3, 3, 3], [2, 2, 2, 2], [1, 2, 3, 4],
    [4, 4, 4, 4], [1, 1, 2, 1], [2, 2, 2, 2], [None, 5, 5, 5], [None, None, 1, 1], [None, None, 3, None],
]


class Alpha(unittest.TestCase):
    def test_krippendorff_2011_worked_example(self):
        units = [[v for v in u if v is not None] for u in K2011]
        self.assertAlmostEqual(sr.alpha(units, "nominal"), 0.743, places=3)
        self.assertAlmostEqual(sr.alpha(units, "ordinal"), 0.815, places=3)
        self.assertAlmostEqual(sr.alpha(units, "interval"), 0.849, places=3)

    def test_perfect_agreement_is_one(self):
        self.assertEqual(sr.alpha([[3, 3, 3], [1, 1], [5, 5, 5]], "ordinal"), 1.0)

    def test_no_variation_at_all_is_undefined(self):
        self.assertIsNone(sr.alpha([[3, 3], [3, 3, 3]], "ordinal"))


SINGLE = """Assessment of this chat (6 messages from you; based on 1 chat), against Modo rubric v1.2.
Scored 5 times (as separate sub-tasks); the runs agreed on 4 of 5 capabilities.
This chat shows 3 of 5 capabilities. One more chat with different work could show Delegation.
This chat: Practitioner · Level 2 (at least 3 of 5 capabilities at Level 2 or higher).
One chat is a thin sample: your title comes from 10 scored chats. Run /assess-my-chats in claude.ai.
Task type: Data analysis. Agent session: yes (tools: Bash, Edit). Reused saved work: no.

Verification: Level 5 of 5 (confidence: high; 4 of 5 runs)
  Evidence (checks planned first, message 4): "I'll recompute them in my spreadsheet"
  Evidence (V4b, message 5): "I get 78% and you have 82%"
  Why this level: a tier 5 moment backed by a tier 4 check.
  Next level: keep it up.

**Problem Solving: Level 3 of 5** (confidence: low; 5 of 5 runs)
  Evidence (Gives context, message 1): "for Thursday's product review"
  Next level: state constraints.

Strategic Thinking: Level 2 of 5 (confidence: low; 3 of 5 runs)
  Evidence (mentions purpose, message 1): "Thursday's product review"
  Next level: tie it to a decision.

Workflow Design: Not shown in this chat (5 of 5 runs)
  Next level: state an order of steps.

Delegation: Not shown in this chat (runs disagreed)
  Next level: hand over a scoped piece.

Self-assessment by Claude using Modo rubric v1.2 — not verified."""

MULTI = """Assessment across 3 of your chats (2026-10-22 to 2026-10-30), against Modo rubric v1.2.
Each chat was read and scored by its own agent, 3 or 5 times in one response.
Chats: 3 confirmed, 3 scored, 0 too short (fewer than 4 typed user messages), 0 could not be read; 0 skipped before the list.
3 of 10 chats to your title
Task range: 2 of 8 types. Reused saved work: 0 of 3 chats.

Verification: Level 3 of 5 (confidence: medium; shown in 2 of 3 chats; proven level: Level 3)
  Evidence ("Survey findings", 2026-10-28, message 2): "Show me how you decided that."
  Next level: ...

Problem Solving: Level 1 of 5 (confidence: low; shown in 3 of 3 chats)
  Next level: ...

Workflow Design: Not shown in these chats
Delegation: Not shown in these chats
Strategic Thinking: Not shown in these chats

| # | Chat | Date | Typed messages | Result | P | V | W | D | S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Release notes for six updates | 2026-10-30 | 7 | scored (5 runs) | 5 | 1 | 5 | 4 | – |
| 2 | Survey findings for product review | 2026-10-28 | 6 | scored (3 runs) | 3 | 5 | – | – | 2 |
| 3 | Cover letter | 2026-10-21 | 3 | too short | – | – | – | – | – |

Self-assessment by Claude using Modo rubric v1.2 — not verified."""


def re_sub_title(text, line):
    return "\n".join(line if x.startswith("This chat:") else x for x in text.split("\n"))


class ParseAnswer(unittest.TestCase):
    def test_single_chat_levels_confidence_and_overall(self):
        r = sr.parse_answer(SINGLE)
        self.assertEqual(r["levels"], {"Problem Solving": 3, "Verification": 5, "Workflow Design": "not shown",
                                       "Delegation": "runs disagreed", "Strategic Thinking": 2})
        self.assertEqual(r["confidence"]["Verification"], "high")
        self.assertIsNone(r["confidence"]["Workflow Design"])
        self.assertEqual(r["overall"], "Practitioner")

    def test_single_chat_signals(self):
        self.assertEqual(sr.parse_answer(SINGLE)["signals"],
                         {"task": "Data analysis", "agent": "yes", "reuse": "no"})

    def test_a_missing_signals_line_is_not_an_error(self):
        self.assertIsNone(sr.parse_answer(SINGLE.replace("Task type:", "Kind:"))["signals"])

    def test_the_other_title_forms(self):
        for line, want in (("This chat: No title yet (only 2 of 5 capabilities shown; a title needs at least 3).",
                            "No title yet"),
                           ("**This chat: Delegator · Level 3** (at least 3 of 5 capabilities)", "Delegator"),
                           ("Your title: Orchestrator · Level 4 (reached in at least 3 chats).", "Orchestrator"),
                           ("Your title: No title yet (no title reached in 3 chats).", "No title yet"),
                           ("12 of 10 chats to your title", "12 of 10 chats to your title")):
            text = re_sub_title(SINGLE, line)
            self.assertEqual(sr.parse_answer(text)["overall"], want)

    def test_single_chat_behaviours_by_id_or_short_name(self):
        r = sr.parse_answer(SINGLE)
        self.assertEqual(r["behaviours"]["Verification"], ["V5a", "V4b"])
        self.assertEqual(r["behaviours"]["Problem Solving"], ["P3a"])
        self.assertEqual(r["behaviours"]["Strategic Thinking"], ["S2a"])
        self.assertEqual(r["behaviours"]["Workflow Design"], [])

    def test_multi_chat_combined_levels(self):
        r = sr.parse_answer(MULTI)
        self.assertEqual(r["levels"]["Verification"], 3)
        self.assertEqual(r["levels"]["Delegation"], "not shown")
        self.assertEqual(r["overall"], "3 of 10 chats to your title")
        self.assertEqual(r["rubric"], "v1.2")

    def test_behaviour_names_in_another_tense_still_map(self):
        # The skill's own example label is "checked a fact"; the rubric says "Checks a fact".
        text = SINGLE.replace("(V4b, message 5)", "(checked a fact, message 5)")
        self.assertEqual(sr.parse_answer(text)["behaviours"]["Verification"], ["V5a", "V3b"])
        text = SINGLE.replace("(V4b, message 5)", "(asked for the working, message 5)")
        self.assertEqual(sr.parse_answer(text)["behaviours"]["Verification"], ["V5a", "V4a"])

    def test_missing_capability_is_an_error(self):
        with self.assertRaises(sr.ParseError):
            sr.parse_answer(SINGLE.replace("Strategic Thinking: Level 2", "Strategic stuff"))

    def test_missing_overall_is_an_error(self):
        with self.assertRaises(sr.ParseError):
            sr.parse_answer(SINGLE.replace("This chat:", "The chat:"))


def run(chat, levels, overall, behaviours=None, kind="single", n=0):
    caps = sr.CAPS
    return {"chat": chat, "kind": kind, "run": n, "model": "test", "rubric": "v1.2",
            "levels": dict(zip(caps, levels)), "overall": overall,
            "behaviours": behaviours or {c: [] for c in caps}}


NS = "not shown"
# Chat "a": 5 runs. P steady at 3; V 4,4,4,5,4; W never shown; D shown in 4 of 5;
# S 2,4,2,2,2 (spread 2). Titles: Delegator 4 times, Practitioner once.
A = [run("a", [3, 4, NS, 3, 2], "Delegator", {"Problem Solving": ["P3a"], "Verification": ["V4b", "V3a"],
                                             "Workflow Design": [], "Delegation": ["D3a"], "Strategic Thinking": []}),
     run("a", [3, 4, NS, 3, 4], "Delegator", {"Problem Solving": ["P3a"], "Verification": ["V4b"],
                                             "Workflow Design": [], "Delegation": [], "Strategic Thinking": []}),
     run("a", [3, 4, NS, 3, 2], "Delegator"),
     run("a", [3, 5, NS, NS, 2], "Practitioner"),
     run("a", [3, 4, NS, 3, 2], "Delegator")]
GOLDEN = {"a": {"bands": {"Problem Solving": [3], "Verification": [4, 5], "Workflow Design": [NS],
                          "Delegation": [3, 4], "Strategic Thinking": [2]},
                "overall": ["Delegator"]}}


class Analyse(unittest.TestCase):
    def setUp(self):
        self.m = sr.analyse(A, GOLDEN)
        self.cell = {(c["chat"], c["capability"]): c for c in self.m["cells"]}

    def test_spread_same_level_rate_and_flips_per_capability(self):
        v = self.cell[("a", "Verification")]
        self.assertEqual((v["spread"], v["same_level"], v["flips"]), (1, 0.8, 0.0))
        d = self.cell[("a", "Delegation")]
        self.assertEqual((d["spread"], d["same_level"], d["flips"]), (0, 0.8, 0.2))
        s = self.cell[("a", "Strategic Thinking")]
        self.assertEqual(s["spread"], 2)
        self.assertEqual(self.cell[("a", "Workflow Design")]["seen"], {NS: 5})

    def test_band_accuracy(self):
        self.assertEqual(self.cell[("a", "Delegation")]["accuracy"], 0.8)
        self.assertEqual(self.cell[("a", "Strategic Thinking")]["accuracy"], 0.8)
        # 25 run-capability results, 2 outside their band (D not shown once, S at 4 once).
        self.assertEqual(self.m["accuracy"], 23 / 25)

    def test_title_agreement_and_title_accuracy(self):
        t = self.m["titles"]["a"]
        self.assertEqual((t["agreement"], t["accuracy"]), (0.8, 0.8))
        self.assertEqual(t["seen"], {"Delegator": 4, "Practitioner": 1})

    def test_behaviour_share_across_runs(self):
        self.assertEqual(self.cell[("a", "Verification")]["behaviours"], {"V4b": 0.4, "V3a": 0.2})

    def test_pass_fail_against_the_bar(self):
        verdict = {r["metric"]: r["pass"] for r in self.m["bar"]}
        self.assertFalse(verdict["spread"])         # S spread 2
        self.assertTrue(verdict["same_level"])      # every cell at 0.8 or more
        self.assertFalse(verdict["title"])          # 0.8 < 0.9
        self.assertFalse(verdict["flips"])          # D flips 0.2 > 0.1
        self.assertTrue(verdict["accuracy"])        # 0.92
        self.assertIn("alpha", verdict)

    def test_multi_chat_runs_get_their_own_spread_and_title_check(self):
        multi = [run("set", [2, 3, NS, 2, 3], "Practitioner", kind="multi", n=i) for i in range(3)]
        multi[2]["levels"]["Verification"] = 4
        m = sr.analyse(A + multi, GOLDEN)
        verdict = {r["metric"]: r for r in m["bar"]}
        self.assertTrue(verdict["multi_spread"]["pass"])
        self.assertTrue(verdict["multi_title"]["pass"])
        self.assertNotIn(("set", "Verification"), {(c["chat"], c["capability"]) for c in m["cells"]
                                                    if c["kind"] == "single"})


def johnny_golden():
    bands = {c: None for c in sr.CAPS}
    bands["Verification"] = [3, 4, 5]
    bands["Delegation"] = [1, 2, 3]
    return {"j": {"bands": bands, "overall": ["Delegator"], "title_source": "johnny",
                  "scores": {"Verification": 4, "Delegation": 2}}}


class JohnnysExamples(unittest.TestCase):
    """Every disagreement with his title or a level off by 2+ is listed (ticket 35, D8)."""

    def runs(self, *rows):
        return [run("j", levels, title, n=i) for i, (levels, title) in enumerate(rows)]

    def test_a_match_lists_nothing(self):
        m = sr.analyse(self.runs(([3, 4, 3, 3, 2], "Delegator"), ([3, 5, 3, 1, 2], "Delegator")), johnny_golden())
        row = m["johnny"][0]
        self.assertEqual((row["chat"], row["title_match"], row["off"]), ("j", True, []))

    def test_a_wrong_title_in_any_run_is_listed(self):
        m = sr.analyse(self.runs(([3, 4, 3, 3, 2], "Delegator"), ([3, 4, 3, 3, 2], "Practitioner")), johnny_golden())
        self.assertFalse(m["johnny"][0]["title_match"])
        self.assertEqual(m["johnny"][0]["titles"], {"Delegator": 1, "Practitioner": 1})

    def test_a_level_off_by_two_is_listed(self):
        m = sr.analyse(self.runs(([3, 2, 3, 2, 2], "Delegator"), ([3, 4, 3, 2, 2], "Delegator")), johnny_golden())
        self.assertEqual(m["johnny"][0]["off"], [{"capability": "Verification", "johnny": 4, "seen": {2: 1}}])

    def test_not_shown_where_he_gave_a_score_is_off(self):
        m = sr.analyse(self.runs(([3, 4, 3, "not shown", 2], "Delegator"),), johnny_golden())
        self.assertEqual(m["johnny"][0]["off"], [{"capability": "Delegation", "johnny": 2, "seen": {"not shown": 1}}])

    def test_markdown_section(self):
        md = sr.markdown(sr.analyse(self.runs(([3, 2, 3, 2, 2], "Practitioner"),), johnny_golden()))
        self.assertIn("## Johnny's examples", md)
        self.assertIn("| j | Delegator | Practitioner ×1 | no | Verification: his 4, seen 2 ×1 |", md)
        self.assertIn("Sumeet decides", md)

    def test_titles_from_johnny_are_not_taken_from_our_rule(self):
        golden = sr.load_golden()
        self.assertEqual(golden["johnny-d1"]["title_source"], "johnny")
        self.assertEqual(golden["johnny-d1"]["overall"], ["Delegator"])
        self.assertEqual(golden["johnny-o1"]["overall"], ["Orchestrator"])
        self.assertIsNone(golden["johnny-e1"]["bands"]["Verification"])
        self.assertEqual(golden["johnny-e1"]["bands"]["Problem Solving"], [1, 2])

    def test_a_chat_with_no_band_counts_for_no_accuracy(self):
        m = sr.analyse(self.runs(([3, 4, 3, 2, 2], "Delegator"),), johnny_golden())
        cell = next(c for c in m["cells"] if c["capability"] == "Problem Solving")
        self.assertIsNone(cell["accuracy"])


class Signals(unittest.TestCase):
    def test_table_of_what_each_run_said(self):
        runs = [dict(run("a", [3, 3, 3, 3, 3], "Delegator", n=i),
                     signals={"task": "Coding", "agent": a, "reuse": "no"}) for i, a in enumerate(("yes", "yes", "no"))]
        m = sr.analyse(runs, {})
        self.assertEqual(m["signals"]["a"], {"agent": {"yes": 2, "no": 1}, "task": {"Coding": 3}, "reuse": {"no": 3}})
        self.assertIn("| a | yes ×2, no ×1 | Coding ×3 | no ×3 |", sr.markdown(m))


class Markdown(unittest.TestCase):
    def test_report_lists_every_metric_with_pass_or_fail(self):
        md = sr.markdown(sr.analyse(A, GOLDEN))
        for words in ("Spread per capability", "Same-level rate", "Overall title agreement",
                      "Shown / not-shown flips", "Accuracy vs expected band", "Krippendorff"):
            self.assertIn(words, md)
        self.assertRegex(md, r"\| Overall title agreement \|.*\| FAIL \|")
        self.assertIn("V4b 40%", md)



class Records(unittest.TestCase):
    def test_reads_every_stab_run_and_flags_unreadable_ones(self):
        import json
        import tempfile
        result = {"cases": [
            {"name": "stab-strong-verifier", "arms": {"with": [
                {"graders": [{"type": "llm", "evidence": SINGLE}]},
                {"graders": [{"type": "llm", "evidence": "Sorry, I can't."}]}]}},
            {"name": "stab-multi-set", "arms": {"with": [{"graders": [{"type": "llm", "evidence": MULTI}]}]}},
            {"name": "too-short", "arms": {"with": [{"graders": [{"type": "llm", "evidence": SINGLE}]}]}}]}
        with tempfile.TemporaryDirectory() as t:
            f = pathlib.Path(t) / "aggregate-result.json"
            f.write_text(json.dumps(result))
            rs = sr.records(f, model="opus")
        self.assertEqual([(r["chat"], r["kind"], r["run"]) for r in rs],
                         [("strong-verifier", "single", 1), ("strong-verifier", "single", 2),
                          ("multi-set", "multi", 1)])
        self.assertEqual(rs[0]["levels"]["Verification"], 5)
        self.assertEqual(rs[0]["model"], "opus")
        self.assertIn("error", rs[1])

    def test_model_flag_with_a_space_or_equals(self):
        import contextlib
        import io
        import json
        import tempfile
        result = {"cases": [{"name": "stab-strong-verifier", "arms": {"with": [
            {"graders": [{"type": "llm", "evidence": SINGLE}]}]}}]}
        with tempfile.TemporaryDirectory() as t:
            f = pathlib.Path(t) / "aggregate-result.json"
            f.write_text(json.dumps(result))
            for argv in (["--model", "opus", str(f)], ["--model=opus", str(f)]):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    sr.main(argv)
                self.assertIn("Models: opus.", out.getvalue())


class GoldenSet(unittest.TestCase):
    """The golden chats are consistent with the published level rule."""

    def test_planted_behaviours_give_levels_inside_the_bands_and_an_expected_title(self):
        from derive_levels import derive, overall
        for cid, chat in sr.golden_chats().items():
            if "planted" not in chat:
                continue
            with self.subTest(chat=cid):
                n = len(chat["turns"])
                self.assertGreaterEqual(n, 4)
                levels = {cap: derive([tuple(x) for x in chat["planted"][cap]], n)[0] for cap in sr.CAPS}
                for cap in sr.CAPS:
                    self.assertIn(levels[cap], chat["expected"]["bands"][cap], cap)
                title = overall(levels, chat["expected"]["agent_session"])["title"] or sr.NO_TITLE
                self.assertIn(title, chat["expected"]["overall"])
                self.assertTrue(set(chat["expected"]["reasons"]) >= set(sr.CAPS) | {"overall"})

    def test_our_expected_titles_are_exactly_the_titles_the_bands_allow(self):
        import itertools
        from derive_levels import overall
        for cid, chat in sr.golden_chats().items():
            if chat["expected"].get("title_source") == "johnny":
                continue
            with self.subTest(chat=cid):
                reach = {overall(dict(zip(sr.CAPS, combo)), chat["expected"]["agent_session"])["title"] or sr.NO_TITLE
                         for combo in itertools.product(*(chat["expected"]["bands"][cap] for cap in sr.CAPS))}
                self.assertEqual(reach, set(chat["expected"]["overall"]))

    def test_johnnys_eight_examples_with_his_scores_bands_and_titles(self):
        from derive_levels import overall
        from test_johnny_rules import EXAMPLES
        chats = sr.golden_chats()
        for name, (levels, agent, title, _) in EXAMPLES.items():
            with self.subTest(name):
                e = chats["johnny-" + name.lower()]["expected"]
                self.assertEqual(e["overall"], [title])
                self.assertEqual(e["agent_session"], agent)
                self.assertEqual(e["title_source"], "johnny")
                scored = {c: lv for c, lv in zip(sr.CAPS, levels) if isinstance(lv, int)}
                self.assertEqual(e["johnny_scores"], scored)
                for cap in sr.CAPS:
                    if cap in scored:
                        self.assertEqual(e["bands"][cap], [v for v in (scored[cap] - 1, scored[cap], scored[cap] + 1)
                                                           if 1 <= v <= 5])
                    else:
                        self.assertIsNone(e["bands"][cap])
                self.assertEqual(overall(e["johnny_scores"], agent)["title"], title)

    def test_johnnys_edge_cases_are_in_the_set(self):
        chats = sr.golden_chats()
        self.assertEqual(chats["johnny-edge-fact-check"]["expected"]["overall"], ["No title yet"])
        self.assertEqual(chats["johnny-edge-plain-chat"]["expected"]["overall"], ["Delegator"])
        claim = chats["johnny-edge-claim"]
        self.assertFalse(claim["expected"]["agent_session"])
        self.assertIn("12 people on my team use my agent", claim["turns"][0]["user"])
        for cid in ("johnny-edge-fact-check", "johnny-edge-plain-chat", "johnny-edge-claim"):
            self.assertIn("written for ticket 35", chats[cid]["source"])
            self.assertGreaterEqual(len(chats[cid]["turns"]), 4)

    def test_johnnys_chats_are_user_messages_with_a_placeholder_reply(self):
        for cid, chat in sr.golden_chats().items():
            if cid.startswith("johnny-") and "edge" not in cid:
                with self.subTest(cid):
                    self.assertIn("Johnny, AI Fluency Levels scoring rules v1", chat["source"])
                    self.assertEqual({t["assistant"] for t in chat["turns"]},
                                     {"(Claude's reply is not part of this example.)"})

    def test_multi_set_expectation_holds_the_planted_combined_result(self):
        import aggregate_chats
        from derive_levels import derive
        chats = sr.golden_chats()
        picked = []
        for cid in sr.MULTI_SET_CHATS:
            c = chats[cid]
            lv = {sr.KEYS[cap]: derive([tuple(x) for x in c["planted"][cap]], len(c["turns"]))[0] for cap in sr.CAPS}
            picked.append((c["updated_at"], {k: ("not_shown" if v == sr.NOT_SHOWN else v) for k, v in lv.items()}))
        got = aggregate_chats.combine(picked)["capabilities"]
        exp = sr.load_golden()[sr.MULTI_SET]
        for cap in sr.CAPS:
            self.assertIn(got[sr.KEYS[cap]]["level"], exp["bands"][cap], cap)
        self.assertEqual(exp["overall"], ["6 of 10 chats to your title"])



class GeneratedCases(unittest.TestCase):
    def test_one_case_per_golden_chat_plus_the_multi_set(self):
        import json
        import gen_stability_evals as gen
        cases = gen.all_cases()
        chats = sr.golden_chats()
        self.assertEqual(set(cases), {"stab-" + c for c in chats} | {"stab-" + sr.MULTI_SET})
        for cid, chat in chats.items():
            rows = [json.loads(x) for x in cases["stab-" + cid]["history.jsonl"].splitlines()]
            self.assertEqual([r["message"]["content"] for r in rows if r["type"] == "user"],
                             [t["user"] for t in chat["turns"]])
        for name, files in cases.items():
            skill = "assess-my-chats" if name.endswith(sr.MULTI_SET) else "assess-my-ai-work"
            self.assertIn(skill, files["graders/skill-fired.md"])
        multi = cases["stab-" + sr.MULTI_SET]
        listed = json.loads(multi["mocks/chats/recent_chats.md"])["chats"]
        self.assertEqual(len(listed), len(sr.MULTI_SET_CHATS))
        for c in listed:
            self.assertIn(f"mocks/chats/fixtures/{c['chat_id']}.json", multi)


if __name__ == "__main__":
    unittest.main()
