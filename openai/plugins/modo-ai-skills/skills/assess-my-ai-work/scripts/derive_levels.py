"""Reference implementation of the Modo AI Skills rubric v1.2 level rule (stdlib only).

Claude applies the rule from the rubric text itself
(plugins/modo-ai-skills/skills/assess-my-ai-work/rubric-v1.2.md); this file
exists so the published rule can be tested. scripts/test_derive_levels.py
replays the rubric's worked examples against it and checks that the behaviour
table here matches the rubric's.

    derive(seen, user_messages)   one run, one capability -> (level, confidence)
    combine(runs)                 3 or 5 runs of one capability -> final result
    coverage(levels)              the coverage line for a result, or None
    overall(levels, agent_session)  the title for one chat, from 5 levels and whether it was an agent session
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
Optional "agent_session": [true, false, true], each run's answer to whether the
user directed an agent or tools in this chat, one per run; most runs decide,
and without it the answer is no (no evidence = no).
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


# The title for one chat. Source: Johnny's scoring rules v1, 2026-11-04
# ("AI Fluency Levels: scoring rules v1", section 1), which replaced the rule
# from 2026-11-03. Give the highest title whose rule is met:
#   Orchestrator, Level 4: 3 of 5 capabilities at 4+, including Delegation, and
#       an agent session (the user directing an agent or tools).
#   Delegator, Level 3: 3 of 5 at 3+, including Delegation.
#   Practitioner, Level 2: 3 of 5 at 2+.
#   Explorer, Level 1: 3 of 5 shown at any level.
#   No title yet: fewer than 3 shown.
# "not shown" and "runs disagreed" reach no level. Scores that reach Orchestrator
# with no agent session give Delegator with a note (ticket 35, D9). Multiplier
# comes later: it needs Modo sharing data, and a claim in a chat is not evidence.
# The title is not stored in the record.
LADDER = {1: "Explorer", 2: "Practitioner", 3: "Delegator", 4: "Orchestrator", 5: "Multiplier"}
NO_TITLE = "No title yet"
OVERALL_MIN_CAPABILITIES = 3
OVERALL_TOP_FROM_CHATS = 4
DELEGATION_FROM_LEVEL = 3
MULTIPLIER_NOTE = ("Level 5 (Multiplier) comes later: it needs Modo sharing data that a chat doesn't hold, "
                   "and a claim in a chat is not evidence.")
NO_AGENT_NOTE = "The title stops at Delegator: no agent work visible in this chat."


def _is_level(v):
    return isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 5


def overall(levels, agent_session=False):
    """The title for one chat from its five capability levels.

    levels: the five levels in rubric order, or a mapping of capability name or
    key -> level; each is 1-5 or a word ("not shown", "not_shown", "runs
    disagreed"). agent_session: the user directed an agent or tools in this chat.
    Returns {"level": 1-4 or None, "title": the ladder name or None, "line": the
    title line, "note": one more line, or None}.
    """
    if isinstance(levels, dict):
        values = list(levels.values())
        delegation = levels.get("Delegation", levels.get("delegation"))
    else:
        values = list(levels)
        delegation = values[3]
    shown = [v for v in values if _is_level(v)]

    def met(n):
        return sum(1 for v in shown if v >= n) >= OVERALL_MIN_CAPABILITIES and (
            n < DELEGATION_FROM_LEVEL or (_is_level(delegation) and delegation >= n))

    level = max((n for n in range(1, OVERALL_TOP_FROM_CHATS + 1) if met(n)), default=None)
    if level is None:
        return {"level": None, "title": None, "note": None,
                "line": (f"This chat: {NO_TITLE} (only {len(shown)} of 5 capabilities shown; "
                         f"a title needs at least {OVERALL_MIN_CAPABILITIES}).")}
    note = None
    if level == OVERALL_TOP_FROM_CHATS:
        if agent_session:
            note = MULTIPLIER_NOTE
        else:
            level, note = OVERALL_TOP_FROM_CHATS - 1, NO_AGENT_NOTE
    why = f"at least {OVERALL_MIN_CAPABILITIES} of 5 capabilities " + (
        f"at Level {level} or higher" if level > 1 else "shown")
    if level >= DELEGATION_FROM_LEVEL:
        why += ", including Delegation"
    if level == OVERALL_TOP_FROM_CHATS:
        why += ", with agent work shown"
    return {"level": level, "title": LADDER[level], "note": note,
            "line": f"This chat: {LADDER[level]} \u00b7 Level {level} ({why})."}


CAPABILITIES = {"Problem Solving": "P", "Verification": "V", "Workflow Design": "W",
                "Delegation": "D", "Strategic Thinking": "S"}
SCRIPT_VERSION = "rubric-v1.2-levels-1"


class RunsError(ValueError):
    pass


def _norm(text):
    return " ".join(str(text).split())


def _runs_seen(data):
    if not isinstance(data, dict) or not {"user_messages", "runs"} <= set(data) or \
            set(data) - {"user_messages", "runs", "messages", "run_kind", "agent_session"}:
        raise RunsError('expected {"user_messages": N, "runs": [...]} with optional "messages", "run_kind", '
                        '"agent_session"')
    n, runs, messages = data["user_messages"], data["runs"], data.get("messages")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise RunsError("user_messages must be a positive integer")
    if messages is not None and not (isinstance(messages, list) and len(messages) == n
                                     and all(isinstance(m, str) for m in messages)):
        raise RunsError("messages must be the list of the user's N messages, in order")
    if not isinstance(runs, list) or len(runs) not in (3, 5):
        raise RunsError("runs must be a list of 3 or 5 runs")
    votes = data.get("agent_session", [])
    if "agent_session" in data and not (isinstance(votes, list) and len(votes) == len(runs)
                                        and all(isinstance(v, bool) for v in votes)):
        raise RunsError("agent_session must be a list of true or false, one per run")
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
    votes = data.get("agent_session", [])
    agent_session = sum(votes) > len(votes) / 2
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
            "agent_session": agent_session,
            "overall": overall([result[c]["level"] for c in CAPABILITIES], agent_session),
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
        (overall([3, 4, 5, 4, 2])["level"], 3),                     # Orchestrator scores, no agent
        (overall([5, 5, 5, 5, 5], True)["level"], 4),               # Level 5 is never given from chats
        (overall([3, 3, 3, 2, 3], True)["level"], 2),               # Level 3 needs Delegation
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
