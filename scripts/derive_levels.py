"""Reference implementation of the Modo AI Skills rubric v1.1 level rule (stdlib only).

Claude applies the rule from the rubric text itself
(plugins/modo-ai-skills/skills/assess-my-ai-work/rubric-v1.1.md); this file
exists so the published rule can be tested. scripts/test_derive_levels.py
replays the rubric's worked examples against it and checks that the behaviour
table here matches the rubric's.

    derive(seen, user_messages)   one run, one capability -> (level, confidence)
    combine(runs)                 3 or 5 runs of one capability -> final result
    coverage(levels)              the coverage line for a result, or None
    assess(data)                  all runs of a chat -> every level, as JSON

Command line (the ChatGPT version runs this in its code tool, so the levels come
from this arithmetic, not from the model's reading of the rule):

    python3 derive_levels.py runs.json      # or the JSON on stdin

runs.json: {"user_messages": 7, "runs": [RUN, RUN, RUN]} where each RUN maps
a capability name to the behaviours noted in that run, as [message, id] pairs:
{"Verification": [[2, "V4b"], [6, "V5a"]], "Delegation": [[7, "D1u"]], ...}.
A capability with nothing noted may be left out or given [].
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


CAPABILITIES = {"Problem Solving": "P", "Verification": "V", "Workflow Design": "W",
                "Delegation": "D", "Strategic Thinking": "S"}


class RunsError(ValueError):
    pass


def _runs_seen(data):
    if not isinstance(data, dict) or set(data) != {"user_messages", "runs"}:
        raise RunsError('expected exactly {"user_messages": N, "runs": [...]}')
    n, runs = data["user_messages"], data["runs"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise RunsError("user_messages must be a positive integer")
    if not isinstance(runs, list) or len(runs) not in (3, 5):
        raise RunsError("runs must be a list of 3 or 5 runs")
    out = []
    for i, run in enumerate(runs, 1):
        if not isinstance(run, dict) or set(run) - set(CAPABILITIES):
            raise RunsError(f"run {i}: keys must be capability names {list(CAPABILITIES)}")
        per_cap = {}
        for cap, prefix in CAPABILITIES.items():
            pairs = run.get(cap, [])
            seen = []
            for pair in pairs if isinstance(pairs, list) else [None]:
                if not (isinstance(pair, list) and len(pair) == 2):
                    raise RunsError(f"run {i}, {cap}: each behaviour is [message, id]")
                m, b = pair
                if not isinstance(m, int) or isinstance(m, bool) or not 1 <= m <= n:
                    raise RunsError(f"run {i}, {cap}: message {m!r} is not 1 to {n}")
                if b not in BEHAVIOURS or not b.startswith(prefix):
                    raise RunsError(f"run {i}, {cap}: {b!r} is not a {cap} behaviour id")
                seen.append((m, b))
            per_cap[cap] = sorted(seen)
        out.append(per_cap)
    return n, out


def assess(data):
    """Every level of one chat from all its runs: the final result per capability."""
    n, runs = _runs_seen(data)
    result, levels = {}, {}
    for cap in CAPABILITIES:
        derived = [derive(run[cap], n) for run in runs]
        final = combine(derived)
        final["runs"] = [lvl for lvl, _ in derived]
        result[cap] = final
        levels[cap] = NOT_SHOWN if final["level"] == DISAGREED else final["level"]
    shown_for_coverage = {c: (lvl if result[c]["level"] != DISAGREED else 1) for c, lvl in levels.items()}
    differ = any(len(set(result[c]["runs"])) > 1 for c in CAPABILITIES)
    return {"capabilities": result, "coverage": coverage(shown_for_coverage),
            "runs_agree": not differ,
            "needs_more_runs": len(runs) == 3 and differ}


if __name__ == "__main__":
    raw = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    try:
        print(json.dumps(assess(json.loads(raw)), indent=2))
    except (RunsError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
