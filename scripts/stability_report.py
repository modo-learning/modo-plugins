"""Stability (test-retest) report for Modo AI Skills scoring (ticket 33, stdlib only).

Reads the aggregate-result.json files of `claude plugin eval` runs of the
stab-* cases (plugins/modo-ai-skills/evals-stability/, written by
scripts/gen_stability_evals.py), reads each run's final answer, and writes a
Markdown report with every metric of the ticket and pass or fail against the
proposed pass bar, using the golden chats' expected bands
(scripts/fixtures/stability/*/chat.json). Exit 1 if any metric fails.

    claude plugin eval plugins/modo-ai-skills --eval-dir evals-stability --case 'stab-*' \
        --runs 5 --model opus --ablation none --no-publish --output-dir /tmp/stab
    python3 scripts/stability_report.py --model=opus /tmp/stab/aggregate-result.json > docs/stability/<date>.md

Summary statistic: Krippendorff's alpha, ordinal metric, over the units
(chat, capability) with each run as an observer and the numeric level as the
value ("not shown" counts as missing for alpha; it is measured by the flips
metric instead). Formula (Krippendorff, K. 2011, "Computing Krippendorff's
Alpha-Reliability", Annenberg School for Communication, University of
Pennsylvania):

    alpha = 1 - (n - 1) * sum_ck o_ck * d2_ck / sum_ck n_c * n_k * d2_ck

with o_ck the coincidence matrix (each pair of values in a unit with m_u
values adds 1 / (m_u - 1)), n_c its marginals, n their total, and for the
ordinal metric d2_ck = (sum_{g=c..k} n_g - (n_c + n_k) / 2) ** 2.
"""

import itertools
import json
import pathlib
import re
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import aggregate_chats  # noqa: E402
import derive_levels  # noqa: E402
from check_eval_records import final_text  # noqa: E402


def _delta2(metric, c, k, marg):
    if metric == "nominal":
        return 0.0 if c == k else 1.0
    if metric == "interval":
        return float(c - k) ** 2
    if metric == "ordinal":
        lo, hi = min(c, k), max(c, k)
        return (sum(n for g, n in marg.items() if lo <= g <= hi) - (marg[c] + marg[k]) / 2) ** 2
    raise ValueError(metric)


def alpha(units, metric="ordinal"):
    """Krippendorff's alpha. units: list of lists of the values given to each
    unit (missing values left out). Units with fewer than 2 values are not
    pairable and are dropped. Returns None when there is no variation at all
    (expected disagreement 0), where alpha is undefined."""
    coinc = Counter()
    for u in units:
        m = len(u)
        if m < 2:
            continue
        for i, j in itertools.permutations(range(m), 2):
            coinc[(u[i], u[j])] += 1 / (m - 1)
    marg = Counter()
    for (c, _), w in coinc.items():
        marg[c] += w
    n = sum(marg.values())
    values = sorted(marg)
    observed = sum(w * _delta2(metric, c, k, marg) for (c, k), w in coinc.items())
    expected = sum(marg[c] * marg[k] * _delta2(metric, c, k, marg) for c in values for k in values)
    if expected == 0:
        return None
    return 1 - (n - 1) * observed / expected


# ---- Parsing one eval run's final message -------------------------------------

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUBRIC = ROOT / "plugins" / "modo-ai-skills" / "skills" / "assess-my-ai-work" / "rubric-v1.1.md"
CAPS = ("Problem Solving", "Verification", "Workflow Design", "Delegation", "Strategic Thinking")
NOT_SHOWN, DISAGREED = "not shown", "runs disagreed"
NOT_ENOUGH = "not enough shown"
TITLES = ("Explorer", "Practitioner", "Delegator", "Orchestrator")


class ParseError(ValueError):
    pass


def _name_key(label):
    """A behaviour label made tense-blind: "Checked a fact", "checks a fact" and
    "check a fact" give the same key (the skill's own example uses past tense)."""
    return " ".join(re.sub(r"(?:ed|es|s)$", "", w) for w in label.lower().split())


def behaviour_names(rubric=RUBRIC):
    """{label key: id} for every behaviour id and short name in the rubric's tables."""
    out = {}
    for m in re.finditer(r"^\| *([PVWDS]\d[a-z]?) *\| *\d *\| *([^|]+?) *\|", rubric.read_text(), re.M):
        out[m.group(1).lower()] = m.group(1)
        out[_name_key(m.group(2))] = m.group(1)
    return out


_CAP = "|".join(CAPS)
_LEVEL = re.compile(rf"^[*_ ]*({_CAP})[*_ ]*:[*_ ]*Level ([1-5]) of 5[*_ ]*\((?:confidence: (\w+))?", re.M)
_NOT = re.compile(rf"^[*_ ]*({_CAP})[*_ ]*:[*_ ]*Not shown in (?:this chat|these chats)[*_ ]*(\(runs disagreed\))?", re.M)
_OVERALL = re.compile(r"^[*_ ]*Overall:[*_ ]*(?:(" + "|".join(TITLES) + r") \(Level [1-4]|(not enough shown))", re.M)
_EVIDENCE = re.compile(r"^\s*Evidence \(([^,()]+), message \d+\)", re.M)
_RUBRIC = re.compile(r"against Modo rubric (v[\d.]+?)\.?\s*$", re.M)


def parse_answer(text, names=None):
    """One assessment answer (single-chat or multi-chat shape) -> run record:
    {"levels", "confidence", "behaviours", "overall", "rubric"}.
    Raises ParseError when a capability or the overall line is missing."""
    names = names or behaviour_names()
    levels, confidence, spans = {}, {}, []
    for m in _LEVEL.finditer(text):
        levels.setdefault(m.group(1), int(m.group(2)))
        confidence.setdefault(m.group(1), m.group(3))
        spans.append((m.start(), m.group(1)))
    for m in _NOT.finditer(text):
        levels.setdefault(m.group(1), DISAGREED if m.group(2) else NOT_SHOWN)
        confidence.setdefault(m.group(1), None)
        spans.append((m.start(), m.group(1)))
    missing = [c for c in CAPS if c not in levels]
    if missing:
        raise ParseError("no level line for " + ", ".join(missing))
    overall = _OVERALL.search(text)
    if not overall:
        raise ParseError("no Overall line")
    spans.sort()
    behaviours = {c: [] for c in CAPS}
    for i, (start, cap) in enumerate(spans):
        end = spans[i + 1][0] if i + 1 < len(spans) else len(text)
        for m in _EVIDENCE.finditer(text, start, end):
            label = m.group(1).strip()
            bid = names.get(label.lower()) or names.get(_name_key(label))
            if bid and bid not in behaviours[cap]:
                behaviours[cap].append(bid)
    record = {"levels": {c: levels[c] for c in CAPS}, "confidence": {c: confidence[c] for c in CAPS},
              "behaviours": behaviours, "overall": overall.group(1) or overall.group(2)}
    rubric = _RUBRIC.search(text)
    record["rubric"] = rubric.group(1) if rubric else "not specified"
    return record


# ---- Metrics ------------------------------------------------------------------
# Proposed pass bar (ticket 33 Part 4; Angelina and Keith to confirm).
BAR = {"spread": 1, "same_level": 0.8, "title": 0.9, "flips": 0.10, "accuracy": 0.9, "alpha": 0.8,
       "multi_spread": 1, "multi_title": 0.9}


def _shown(v):
    return isinstance(v, int)


def _cell_metrics(values, band):
    n = len(values)
    seen = Counter(values)
    nums = [v for v in values if _shown(v)]
    shown = len(nums)
    return {"n": n, "seen": dict(seen),
            "spread": max(nums) - min(nums) if nums else 0,
            "same_level": max(seen.values()) / n,
            "flips": min(shown, n - shown) / n,
            "accuracy": (sum(1 for v in values if v in band) / n) if band is not None else None}


def analyse(runs, golden):
    """Every metric of the report. runs: run records (see records());
    golden: {chat: {"bands": {capability: [allowed values]}, "overall": [allowed titles]}}."""
    groups = {}
    for r in runs:
        groups.setdefault((r["chat"], r.get("kind", "single")), []).append(r)
    cells, titles = [], {}
    for (chat, kind), rs in sorted(groups.items()):
        g = golden.get(chat)
        for cap in CAPS:
            values = [r["levels"][cap] for r in rs]
            c = _cell_metrics(values, g["bands"][cap] if g else None)
            c["numeric"] = [v for v in values if _shown(v)]
            ids = Counter(b for r in rs for b in set(r.get("behaviours", {}).get(cap, [])))
            c.update(chat=chat, kind=kind, capability=cap,
                     behaviours={b: k / len(rs) for b, k in ids.most_common()})
            cells.append(c)
        seen = Counter(r["overall"] for r in rs)
        titles[chat] = {"kind": kind, "n": len(rs), "seen": dict(seen),
                        "agreement": max(seen.values()) / len(rs),
                        "accuracy": (sum(k for t, k in seen.items() if t in g["overall"]) / len(rs)) if g else None}
    single = [c for c in cells if c["kind"] == "single"]
    multi = [c for c in cells if c["kind"] == "multi"]
    banded = [c for c in single if c["accuracy"] is not None]
    accuracy = (sum(c["accuracy"] * c["n"] for c in banded) / sum(c["n"] for c in banded)) if banded else None
    a = alpha([c["numeric"] for c in single], "ordinal")

    def row(metric, label, value, ok, shown):
        return {"metric": metric, "label": label, "value": value, "pass": ok, "shown": shown}

    def worst(cs, key, fn):
        return fn(c[key] for c in cs) if cs else None

    bar = []
    if single:
        s, sl, fl = worst(single, "spread", max), worst(single, "same_level", min), worst(single, "flips", max)
        tl = min(t["agreement"] for t in titles.values() if t["kind"] == "single")
        bar += [
            row("spread", "Spread per capability across runs", s, s <= BAR["spread"], f"worst {s}; pass ≤ 1"),
            row("same_level", "Same-level rate per capability", sl, sl >= BAR["same_level"],
                f"worst {sl:.0%}; pass ≥ 80%"),
            row("title", "Overall title agreement", tl, tl >= BAR["title"], f"worst {tl:.0%}; pass ≥ 90%"),
            row("flips", "Shown / not-shown flips", fl, fl <= BAR["flips"], f"worst {fl:.0%}; pass ≤ 10%"),
            row("accuracy", "Accuracy vs expected band", accuracy,
                accuracy is not None and accuracy >= BAR["accuracy"],
                "no expected bands" if accuracy is None else f"{accuracy:.0%}; pass ≥ 90%"),
            row("alpha", "Summary reliability (Krippendorff's alpha, ordinal)", a,
                a is not None and a >= BAR["alpha"],
                "undefined (no variation in any level)" if a is None else f"{a:.3f}; pass ≥ 0.8"),
        ]
    if multi:
        ms = worst(multi, "spread", max)
        mt = min(t["agreement"] for t in titles.values() if t["kind"] == "multi")
        bar += [row("multi_spread", "Multi-chat combined levels: spread", ms, ms <= BAR["multi_spread"],
                    f"worst {ms}; pass ≤ 1"),
                row("multi_title", "Multi-chat overall title agreement", mt, mt >= BAR["multi_title"],
                    f"worst {mt:.0%}; pass ≥ 90%")]
    models = sorted({str(r.get("model")) for r in runs})
    return {"cells": cells, "titles": titles, "accuracy": accuracy, "alpha": a, "bar": bar,
            "runs": len(runs), "models": models,
            "rubric": sorted({str(r.get("rubric")) for r in runs})}


# ---- Markdown -----------------------------------------------------------------
def _levels(seen):
    order = sorted(seen, key=lambda v: (not _shown(v), v if _shown(v) else 0, str(v)))
    return ", ".join(f"{v} ×{seen[v]}" for v in order)


def _pct(x):
    return "–" if x is None else f"{x:.0%}"


def markdown(m):
    out = ["# Modo AI Skills stability report", "",
           f"Runs: {m['runs']}. Models: {', '.join(m['models'])}. Rubric: {', '.join(m['rubric'])}.",
           "Pass bar: proposal from ticket 33, Angelina and Keith to confirm.", "",
           "## Pass bar", "", "| Metric | Result | Pass |", "| --- | --- | --- |"]
    out += [f"| {r['label']} | {r['shown']} | {'pass' if r['pass'] else 'FAIL'} |" for r in m["bar"]]
    overall = all(r["pass"] for r in m["bar"]) if m["bar"] else False
    out += ["", f"**Overall: {'PASS' if overall else 'FAIL'}**", ""]
    for kind, heading in (("single", "Single-chat runs"), ("multi", "Multi-chat runs (combined levels)")):
        cs = [c for c in m["cells"] if c["kind"] == kind]
        if not cs:
            continue
        out += [f"## {heading}", "", "| Chat | Capability | Runs | Levels seen | Spread | Same level | Flips | In band |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        out += [f"| {c['chat']} | {c['capability']} | {c['n']} | {_levels(c['seen'])} | {c['spread']} | "
                f"{_pct(c['same_level'])} | {_pct(c['flips'])} | {_pct(c['accuracy'])} |" for c in cs]
        out += ["", "| Chat | Runs | Titles seen | Agreement | In expected |", "| --- | --- | --- | --- | --- |"]
        out += [f"| {chat} | {t['n']} | {', '.join(f'{k} ×{v}' for k, v in t['seen'].items())} | "
                f"{_pct(t['agreement'])} | {_pct(t['accuracy'])} |"
                for chat, t in m["titles"].items() if t["kind"] == kind]
        out.append("")
    out += ["## Behaviour agreement", "",
            "Share of runs whose evidence lines named each behaviour (the answer shows 1 to 3 behaviours per "
            "capability, so this explains level moves but is not a full count).", "",
            "| Chat | Capability | Behaviours |", "| --- | --- | --- |"]
    out += [f"| {c['chat']} | {c['capability']} | "
            f"{', '.join(f'{b} {s:.0%}' for b, s in c['behaviours'].items())} |"
            for c in m["cells"] if c["behaviours"]]
    out += ["", "Flips: a capability withheld because its runs disagreed counts as not shown here (it is what the "
            "user sees), although the overall rule and coverage count it as shown. Multi-chat answers name no "
            "behaviours, so behaviour agreement covers single-chat runs only.",
            "", "Alpha: Krippendorff (2011), \"Computing Krippendorff's Alpha-Reliability\", ordinal metric; "
            "units are (chat, capability), each run is an observer, \"not shown\" is missing.", ""]
    return "\n".join(out)


# ---- Golden set ---------------------------------------------------------------
GOLDEN_DIR = ROOT / "scripts" / "fixtures" / "stability"
MULTI_SET = "multi-set"
KEYS = dict(zip(CAPS, ("problem_solving", "verification", "workflow_design", "delegation", "strategic_thinking")))


def golden_chats(folder=GOLDEN_DIR):
    """{chat id: chat.json content}, every golden chat."""
    return {d["id"]: d for d in (json.loads(p.read_text()) for p in sorted(folder.glob("*/chat.json")))}


def _title(levels):
    t = derive_levels.overall(list(levels))
    return t["title"] or NOT_ENOUGH


def multi_expected(chats):
    """Expected band and titles of the combined result over these chats: every
    combined level and title reachable when each chat's level is any value in
    its band (combined by aggregate_chats.combine, the published rule). Each
    capability is combined on its own, so the bands are found per capability
    and the titles over every mix of them."""
    bands = {}
    for cap in CAPS:
        reach = set()
        for pick in itertools.product(*(c["expected"]["bands"][cap] for c in chats)):
            levels = [(c["updated_at"], {k: (v if k == KEYS[cap] else "not_shown") for k in KEYS.values()})
                      for c, v in zip(chats, ("not_shown" if x == NOT_SHOWN else x for x in pick))]
            got = aggregate_chats.combine(levels)["capabilities"][KEYS[cap]]["level"]
            reach.add(NOT_SHOWN if got == "not_shown" else got)
        bands[cap] = sorted(reach, key=str)
    titles = {_title(combo) for combo in itertools.product(*(bands[cap] for cap in CAPS))}
    return {"bands": bands, "overall": sorted(titles)}


def load_golden(folder=GOLDEN_DIR, multi_set=None):
    """{chat id: {"bands", "overall"}} for every golden chat, plus MULTI_SET
    (the expected combined result over the multi-chat set's chats)."""
    chats = golden_chats(folder)
    out = {k: {"bands": v["expected"]["bands"], "overall": v["expected"]["overall"]} for k, v in chats.items()}
    members = multi_set or MULTI_SET_CHATS
    out[MULTI_SET] = multi_expected([chats[k] for k in members])
    return out


# The 6 chats of the multi-chat set (ticket 33 Part 1). Until real chats are
# added, all 6 are the synthetic and edge-case chats.
MULTI_SET_CHATS = ("strong-verifier", "weak-delegator", "all-level-1", "mixed", "borderline", "thin")


def records(result_path, model=None):
    """Run records from one `claude plugin eval` aggregate-result.json of the
    stab-* cases: one per run, or {"error": ...} when the answer can't be read."""
    data = json.loads(pathlib.Path(result_path).read_text())
    out = []
    for case in data.get("cases", []):
        name = case.get("name", "")
        if not name.startswith("stab-"):
            continue
        chat = name[len("stab-"):]
        for arm_runs in case.get("arms", {}).values():
            for i, r in enumerate(arm_runs, 1):
                base = {"chat": chat, "kind": "multi" if chat == MULTI_SET else "single", "run": i,
                        "model": model or "not pinned"}
                text = final_text(r)
                try:
                    if text is None:
                        raise ParseError("no final message in the result")
                    base.update(parse_answer(text))
                except ParseError as e:
                    base["error"] = str(e)
                out.append(base)
    return out


def main(argv):
    """stability_report.py [--model NAME | --model=NAME] aggregate-result.json [...]"""
    argv = list(argv)
    model = None
    if "--model" in argv:
        i = argv.index("--model")
        model = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    model = next((a.split("=", 1)[1] for a in argv if a.startswith("--model=")), model)
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    all_runs = [r for f in files for r in records(f, model)]
    runs = [r for r in all_runs if "error" not in r]
    errors = [r for r in all_runs if "error" in r]
    m = analyse(runs, load_golden())
    text = markdown(m)
    if errors:
        text += "\n## Runs that could not be read\n\n" + "\n".join(
            f"- {e['chat']} run {e['run']}: {e['error']}" for e in errors) + "\n"
    sys.stdout.write(text)
    return 0 if m["bar"] and all(r["pass"] for r in m["bar"]) and not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
