"""Reference implementation of the Modo AI Skills rubric v1.1 level rule (stdlib only).

Claude applies the rule from the rubric text itself
(plugins/modo-ai-skills/skills/assess-my-ai-work/rubric-v1.1.md); this file
exists so the published rule can be tested. scripts/test_derive_levels.py
replays the rubric's worked examples against it and checks that the behaviour
table here matches the rubric's.

    derive(seen, user_messages)   one run, one capability -> (level, confidence)
    combine(runs)                 3 or 5 runs of one capability -> final result
    coverage(levels)              the coverage line for a result, or None
    overall(levels)               the overall AI fluency level and title, from 5 levels
    assess(data)                  all runs of a chat -> every level, as JSON

Command line (the ChatGPT version runs this in its code tool, so the levels come
from this arithmetic, not from the model's reading of the rule):

    python3 derive_levels.py runs.json      # or the JSON on stdin

runs.json: {"user_messages": 7, "messages": [the user's 7 messages], "runs": [RUN, RUN, RUN]}
where each RUN maps a capability name to the behaviours noted in that run, as
[message, id, "the user's exact words"]:
{"Verification": [[2, "V4b", "I recomputed the tier growth myself"]], ...}.
A capability with nothing noted may be left out or given []. Without
"messages", [message, id] pairs are accepted and quotes are not checked.
Optional "run_kind": "subagents" when each run was a separate sub-task.
"""

import json
import sys

NOT_SHOWN = "not shown"
DISAGREED = "runs disagreed"  # shown as not shown, but counted as shown for coverage
CONFIDENCE = ("low", "medium", "high")

# Behaviour id -> tier, as in the rubric's behaviour tables.
BEHAVIOURS = {
    "P1": 1, "P2a": 2, "P2b": 2, "P3a": 3, "P3b": 3, "P3c": 3, "P4a": 4, "P4b": 4, "P4c": 4, "P5a": 5, "P5b": 5,
    "V1": 1, "V2a": 2, "V3a": 3, "V3b": 3, "V3c": 3, "V4a": 4, "V4b": 4, "V4c": 4, "V5a": 5, "V5b": 5,
    "W1": 1, "W2a": 2, "W3a": 3, "W3b": 3, "W4a": 4, "W4b": 4, "W5a": 5, "W5b": 5,
    "D1": 1, "D1u": 1, "D2a": 2, "D3a": 3, "D3b": 3, "D3c": 3, "D4a": 4, "D4b": 4, "D5a": 5, "D5b": 5,
    "S1": 1, "S2a": 2, "S3a": 3, "S4a": 4, "S4b": 4, "S5a": 5,
}
EXTRA_WEIGHT = "V"                  # Verification's level 5 may be backed by tier 3 (rule 4)
CHECKS = {"D4a", "D4b", "D5b"}      # Delegation 4-5 needs one of these: hand off and check (rule 4)
UNCHECKED = "D1u"                   # an unchecked handoff caps Delegation at 3 (rule 4)


def _lower(confidence, cap):
    return CONFIDENCE[min(CONFIDENCE.index(confidence), CONFIDENCE.index(cap))]


def derive(seen, user_messages):
    """Apply the level rule to one run's behaviours for one capability.

    seen: list of (message number, behaviour id), all of the same capability.
    Returns (level, confidence): level 1-5 or "not shown"; confidence None
    for not shown.
    """
    if not seen:                                                    # rule 1
        return NOT_SHOWN, None
    positive = [(m, b, BEHAVIOURS[b]) for m, b in seen if BEHAVIOURS[b] > 1]
    contrary = {m for m, b in seen if BEHAVIOURS[b] == 1}
    moments = {m for m, _ in seen}

    if len(moments) >= 3:                                           # rule 6
        confidence = "high" if user_messages >= 6 else "medium"
    else:
        confidence = "medium" if len(moments) == 2 else "low"

    if not positive:                                                # rule 2 (rule 5 does not apply)
        return 1, confidence

    relax = 1 if seen[0][1].startswith(EXTRA_WEIGHT) else 0

    def backed(level):
        need = max(3, level - 1 - relax)                            # tier 2 never backs
        return any(m2 != m1 and t2 >= need
                   for m1, _, t1 in positive if t1 >= level
                   for m2, _, t2 in positive)

    level = max(t for _, _, t in positive)                         # rule 3
    while level >= 4 and not backed(level):                         # rule 4
        level -= 1
    if seen[0][1].startswith("D") and level >= 4 and (
            not CHECKS & {b for _, b, _ in positive} or any(b == UNCHECKED for _, b in seen)):
        level = 3

    p = len({m for m, _, _ in positive})                            # rule 5
    if contrary and len(contrary) >= p:
        level, confidence = min(level, 2), "low"
    elif contrary:
        confidence = _lower(confidence, "medium")
    return level, confidence


def combine(runs):
    """Combine the runs of one capability, per "Running it more than once".

    runs: list of (level, confidence) as returned by derive().
    """
    n = len(runs)
    scored = [(lvl, c) for lvl, c in runs if lvl != NOT_SHOWN]
    if n - len(scored) > n / 2:
        return {"level": NOT_SHOWN, "confidence": None, "agreement": f"{n - len(scored)} of {n} runs"}
    levels = sorted(lvl for lvl, _ in scored)
    spread = levels[-1] - levels[0]
    if spread >= 3:
        return {"level": DISAGREED, "confidence": None, "agreement": DISAGREED}
    level = levels[(len(levels) - 1) // 2]
    confidence = min((c for lvl, c in scored if lvl == level), key=CONFIDENCE.index)
    if spread >= 2 or len(scored) < n:
        confidence = "low"
    elif spread == 1:
        confidence = _lower(confidence, "medium")
    k = sum(1 for lvl in levels if lvl == level)
    return {"level": level, "confidence": confidence, "agreement": f"{k} of {n} runs"}


def coverage(levels):
    """The rubric's coverage line. levels: capability name -> level, in rubric order."""
    missing = [name for name, lvl in levels.items() if lvl == NOT_SHOWN]
    shown = len(levels) - len(missing)
    if shown == len(levels):
        return None
    if shown == len(levels) - 1:
        return (f"This chat shows {shown} of 5 capabilities. One more chat with different "
                f"work could show {missing[0]}.")
    return (f"This chat shows only {shown} of 5 capabilities, so this is a partial picture. "
            "Assess 2–3 more chats with different kinds of work to see the rest.")


# The overall AI fluency level. Maintainer note: decided 2026-11-03, flag for
# review (Angelina, Johnny). Source: "AI Fluency Levels" (Modo, Johnny,
# 2026-11-02): "A person's level is where most of their skills sit" and "Score
# a level when the signals hold for 30 days across at least three of the four
# skills". Rule: the highest L in 1..4 such that at least 3 of the 5
# capabilities have a level of L or higher ("not shown" and "runs disagreed"
# do not reach any level). Fewer than 3 capabilities with a level: no overall
# level. Level 5 (Multiplier) is never given from chats: its signals
# ("Adoption by others", "Outcomes and accountability") need cross-user and
# outcome data a chat doesn't hold. The title is not stored in the record;
# it is derived from the capability levels wherever it is shown.
LADDER = {1: "Explorer", 2: "Practitioner", 3: "Delegator", 4: "Orchestrator", 5: "Multiplier"}
OVERALL_MIN_CAPABILITIES = 3
OVERALL_TOP_FROM_CHATS = 4
MULTIPLIER_NOTE = ("Level 5 (Multiplier) is never given from chats: it needs evidence a chat doesn't hold, "
                   "such as assets or agents your colleagues adopt and tracked time saved.")


def overall(levels):
    """The overall AI fluency level from five capability levels.

    levels: the five levels (a list, or a mapping of capability -> level);
    each is 1-5 or a word ("not shown", "not_shown", "runs disagreed").
    Returns {"level": 1-4 or None, "title": ladder name or None,
    "line": the Overall line, "note": the Multiplier note or None}.
    """
    values = list(levels.values()) if isinstance(levels, dict) else list(levels)
    shown = [v for v in values if isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 5]
    level = max((n for n in range(1, OVERALL_TOP_FROM_CHATS + 1)
                 if sum(1 for v in shown if v >= n) >= OVERALL_MIN_CAPABILITIES), default=None)
    if level is None:
        has = "has" if len(shown) == 1 else "have"
        return {"level": None, "title": None, "note": None,
                "line": (f"Overall: not enough shown (only {len(shown)} of your 5 capabilities {has} a level; "
                         f"an overall level needs at least {OVERALL_MIN_CAPABILITIES}).")}
    return {"level": level, "title": LADDER[level],
            "line": (f"Overall: {LADDER[level]} (Level {level} of {OVERALL_TOP_FROM_CHATS} on Modo's AI fluency "
                     f"ladder from chats; at least {OVERALL_MIN_CAPABILITIES} of your 5 capabilities are at "
                     f"Level {level} or higher)."),
            "note": MULTIPLIER_NOTE if level == OVERALL_TOP_FROM_CHATS else None}


CAPABILITIES = {"Problem Solving": "P", "Verification": "V", "Workflow Design": "W",
                "Delegation": "D", "Strategic Thinking": "S"}
SCRIPT_VERSION = "rubric-v1.1-levels-3"


class RunsError(ValueError):
    pass


def _norm(text):
    return " ".join(str(text).split())


def _runs_seen(data):
    if not isinstance(data, dict) or not {"user_messages", "runs"} <= set(data) or \
            set(data) - {"user_messages", "runs", "messages", "run_kind"}:
        raise RunsError('expected {"user_messages": N, "runs": [...]} with optional "messages", "run_kind"')
    n, runs, messages = data["user_messages"], data["runs"], data.get("messages")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise RunsError("user_messages must be a positive integer")
    if messages is not None and not (isinstance(messages, list) and len(messages) == n
                                     and all(isinstance(m, str) for m in messages)):
        raise RunsError("messages must be the list of the user's N messages, in order")
    if not isinstance(runs, list) or len(runs) not in (3, 5):
        raise RunsError("runs must be a list of 3 or 5 runs")
    texts = [_norm(m) for m in messages] if messages is not None else None
    out, dropped = [], []
    for i, run in enumerate(runs, 1):
        if not isinstance(run, dict) or set(run) - set(CAPABILITIES):
            raise RunsError(f"run {i}: keys must be capability names {list(CAPABILITIES)}")
        per_cap = {}
        for cap, prefix in CAPABILITIES.items():
            entries = run.get(cap, [])
            seen = []
            for entry in entries if isinstance(entries, list) else [None]:
                if not (isinstance(entry, list) and len(entry) in (2, 3)):
                    raise RunsError(f"run {i}, {cap}: each behaviour is [message, id, \"exact quote\"]")
                m, b = entry[0], entry[1]
                if not isinstance(m, int) or isinstance(m, bool) or not 1 <= m <= n:
                    raise RunsError(f"run {i}, {cap}: message {m!r} is not 1 to {n}")
                if b not in BEHAVIOURS or not b.startswith(prefix):
                    raise RunsError(f"run {i}, {cap}: {b!r} is not a {cap} behaviour id")
                if texts is not None:
                    quote = _norm(entry[2]) if len(entry) == 3 else ""
                    if not quote or quote not in texts[m - 1]:
                        dropped.append(f"run {i}, {cap}: {b} in message {m} (no exact quote from that message)")
                        continue
                seen.append((m, b))
            per_cap[cap] = sorted(set(seen))
        out.append(per_cap)
    return n, out, dropped


def assess(data):
    """Every level of one chat from all its runs: the final result per capability.

    With "messages", each behaviour must carry the user's exact words from the
    message it names; a behaviour whose quote isn't found is dropped and listed
    (the rubric: a behaviour is noted "with the exact words that show it").
    Runs that are exact copies of each other count once, and the runs line says so.
    """
    n, runs, dropped = _runs_seen(data)
    distinct = [r for k, r in enumerate(runs) if r not in runs[:k]]
    used = runs if len(distinct) > 1 else distinct
    result, levels = {}, {}
    for cap in CAPABILITIES:
        derived = [derive(run[cap], n) for run in used]
        final = combine(derived)
        final["runs"] = [lvl for lvl, _ in derived]
        result[cap] = final
        levels[cap] = NOT_SHOWN if final["level"] == DISAGREED else final["level"]
    shown_for_coverage = {c: (lvl if result[c]["level"] != DISAGREED else 1) for c, lvl in levels.items()}
    agree = sum(1 for c in CAPABILITIES if len(set(result[c]["runs"])) == 1)
    where = "as separate sub-tasks" if data.get("run_kind") == "subagents" else "in this one response"
    if len(used) == 1:
        runs_line = (f"Scored once: the {len(runs)} runs given were identical, so how far runs "
                     "agree was not measured.")
    else:
        runs_line = f"Scored {len(used)} times ({where}); the runs agreed on {agree} of 5 capabilities."
    return {"script_version": SCRIPT_VERSION, "self_check": self_check(),
            "capabilities": result, "coverage": coverage(shown_for_coverage),
            "overall": overall([result[c]["level"] for c in CAPABILITIES]),
            "runs_used": len(used), "runs_line": runs_line,
            "needs_more_runs": len(used) == 3 and agree < 5,
            "dropped": dropped}


def self_check():
    """Known answers of the level rule; a copy of this file that changed the rule fails here."""
    cases = [
        (derive([(2, "V4b"), (6, "V5a")], 7), (5, "medium")),        # Verification's extra weight
        (derive([(6, "D4a"), (7, "D1u")], 7), (2, "low")),           # unchecked handoff + rule 5
        (derive([(1, "D4a"), (3, "D4b"), (5, "D3a")], 7), (4, "high")),
        (derive([(2, "W4a")], 7), (3, "low")),                       # tier 4 needs backing
        (derive([], 7), (NOT_SHOWN, None)),
        (combine([(3, "medium"), (3, "high"), (4, "medium")]),
         {"level": 3, "confidence": "medium", "agreement": "2 of 3 runs"}),
        (combine([(1, "low"), (4, "high"), (2, "low")]),
         {"level": DISAGREED, "confidence": None, "agreement": DISAGREED}),
        (overall([4, 4, 3, 2, NOT_SHOWN])["level"], 3),
        (overall([5, 5, 5, 5, 5])["level"], 4),                     # Level 5 is never given from chats
        (overall([2, NOT_SHOWN, DISAGREED, NOT_SHOWN, 1])["level"], None),
    ]
    bad = [i for i, (got, want) in enumerate(cases, 1) if got != want]
    if bad:
        raise RunsError(f"self check failed (cases {bad}): this copy of derive_levels.py is not the published one")
    return "passed"


if __name__ == "__main__":
    raw = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    try:
        print(json.dumps(assess(json.loads(raw)), indent=2))
    except (RunsError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
