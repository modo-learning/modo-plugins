"""Combine per-chat results into one multi-chat assessment (stdlib only).

PROPOSED RULES, pending product sign-off. The rules are arithmetic on purpose:
the same chat results always give the same combined result, and the model
never "averages by feel".

Input: one entry per confirmed chat: a valid ChatResult (see
validate_chat_result.py), or the agent's {"chat_id": ..., "error": ...} for a
chat that could not be read. Too-short and could-not-be-read chats are counted
but score nothing.

Per capability, over the scored chats where it was shown (level 1 to 5):

- level: the median of the per-chat levels; with an even number, the lower of
  the two middle ones (the rubric's convention: ties go down).
- best_shown: the highest level reached in at least 2 chats; null if no level
  was reached twice (a one-off peak is not a sustained level). For the record
  only (RECORD.md); people see the Proven level below instead.
- confidence:
    high   shown in 3 or more chats and spread (max - min) at most 1
    medium shown in 2 chats with spread at most 1, or in 3+ chats with spread 2
    low    otherwise (shown in only 1 chat, or spread 3 or more)
- trend (only when shown in 4 or more chats): order those chats by date, take
  the median of the earlier half and of the later half (with an odd number,
  the middle chat is left out); "up" if later > earlier, "down" if lower,
  else "flat". With fewer than 4 chats: null.
- chats_shown: in how many scored chats it was shown.
- Not shown in any scored chat: level "not_shown", confidence "low", no best,
  no trend.

Coverage: how many of the five capabilities were shown in at least one chat.

The score sheet, inside one run (Johnny's scoring rules v1, 2026-11-04, section
2; ticket 35). Nothing here is stored and none of it is a record field:

- chat title: derive_levels.overall() of each scored chat's own levels and its
  agent session. A scored chat with no title counts as a scored chat but adds
  no title (D10).
- proven (per capability): the highest level reached in at least 3 chats; null
  if none. Cumulative: 4, 4, 5 gives 4 (D3, D5).
- person title: the highest chat title reached in at least 3 chats, shown once
  there are 10 scored chats (D4). Cumulative: a higher chat title also counts
  toward lower ones (D3). Under 10: "N of 10 chats to your title".
- task range: how many of the 8 task types the scored chats cover.
- reuse: how many scored chats used saved work. Counts only, no names (D11).

D2, D3 and D5 are readings of Johnny's rules, pending his answer.

Usage:
    python3 -I scripts/aggregate_chats.py results.json   # a JSON list, one entry per chat
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rubric_common import CAPABILITIES, LEVEL_NOT_SHOWN, TASK_TYPES  # noqa: E402
from validate_chat_result import validate  # noqa: E402
from derive_levels import LADDER, MULTIPLIER_NOTE, NO_TITLE, OVERALL_TOP_FROM_CHATS, overall  # noqa: E402


# The thresholds. The skill text (assess-my-chats/SKILL.md, step 4), RECORD.md
# and export-assessment/SKILL.md state them in words, since no script runs in
# claude.ai; test_assess_my_chats_skill.py checks the words match these.
BEST_MIN_CHATS = 2      # best_shown: a level reached in at least this many chats
HIGH_MIN_CHATS = 3      # high confidence: shown in at least this many chats ...
CLOSE_SPREAD = 1        # ... with a spread of at most this
MEDIUM_CHATS = 2        # medium: shown in exactly this many chats with a close spread,
MEDIUM_SPREAD = 2       # or in HIGH_MIN_CHATS or more with exactly this spread
TREND_MIN_CHATS = 4     # trend: only when shown in at least this many chats
PROVEN_MIN_CHATS = 3    # proven level and person title: reached in at least this many chats
TITLE_MIN_CHATS = 10    # person title: shown from this many scored chats


def lower_median(values):
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


def combined_confidence(levels):
    n, spread = len(levels), max(levels) - min(levels)
    if n >= HIGH_MIN_CHATS and spread <= CLOSE_SPREAD:
        return "high"
    if (n == MEDIUM_CHATS and spread <= CLOSE_SPREAD) or (n >= HIGH_MIN_CHATS and spread == MEDIUM_SPREAD):
        return "medium"
    return "low"


def best_shown(levels):
    repeated = [lvl for lvl in set(levels) if levels.count(lvl) >= BEST_MIN_CHATS]
    return max(repeated) if repeated else None


def reached_in(levels):
    """The highest level reached in at least PROVEN_MIN_CHATS of these, counting
    higher levels toward lower ones; None if none. levels: integers."""
    return max((n for n in set(levels) if sum(1 for v in levels if v >= n) >= PROVEN_MIN_CHATS), default=None)


def person_title(chat_title_levels):
    """The person title from each scored chat's title level (None = no title)."""
    n = len(chat_title_levels)
    if n < TITLE_MIN_CHATS:
        return {"level": None, "title": None, "note": None, "line": f"{n} of {TITLE_MIN_CHATS} chats to your title"}
    level = reached_in([v for v in chat_title_levels if v is not None])
    if level is None:
        return {"level": None, "title": None, "note": None,
                "line": f"Your title: {NO_TITLE} (no title reached in {PROVEN_MIN_CHATS} chats)."}
    return {"level": level, "title": LADDER[level],
            "note": MULTIPLIER_NOTE if level == OVERALL_TOP_FROM_CHATS else None,
            "line": f"Your title: {LADDER[level]} \u00b7 Level {level} (reached in at least {PROVEN_MIN_CHATS} chats)."}


def trend(dated):
    if len(dated) < TREND_MIN_CHATS:
        return None
    levels = [lvl for _, lvl in sorted(dated, key=lambda d: d[0])]
    half = len(levels) // 2
    earlier, later = lower_median(levels[:half]), lower_median(levels[-half:])
    return "up" if later > earlier else "down" if later < earlier else "flat"


def failed(result):
    """A chat whose agent returned no ChatResult: {"chat_id": ..., "error": ...} (brief, step 1), or nothing."""
    return not isinstance(result, dict) or "error" in result


def combine(chats):
    """The combined capabilities and coverage for the scored chats.

    chats: (date, levels) per scored chat, levels = {capability key: 1-5 or
    "not_shown"}; date is an ISO date or timestamp. The trend orders the chats
    by date, oldest first (a stable sort: chats with the same date keep the
    order given). aggregate() and validate_assessment_record.py both use this.
    """
    capabilities = {}
    for cap in CAPABILITIES:
        dated = [(date, levels[cap]) for date, levels in chats if levels[cap] != LEVEL_NOT_SHOWN]
        shown = [lvl for _, lvl in dated]
        if not shown:
            capabilities[cap] = {"level": LEVEL_NOT_SHOWN, "confidence": "low", "best_shown": None,
                                 "trend": None, "chats_shown": 0}
            continue
        capabilities[cap] = {"level": lower_median(shown), "confidence": combined_confidence(shown),
                             "best_shown": best_shown(shown), "trend": trend(dated),
                             "chats_shown": len(shown)}
    return {"coverage": sum(1 for c in capabilities.values() if c["level"] != LEVEL_NOT_SHOWN),
            "capabilities": capabilities}


def aggregate(results):
    """Combine the ChatResults of the confirmed chats, failed reads included.

    "chats_assessed", "capabilities" and "coverage" are the record's. The
    output also holds the score sheet, which is not a record field:
    "chat_titles" (one entry per result, None when not scored), "proven",
    "person", "task_range" and "reuse".

    The counts use the multi-chat record's names (RECORD.md, chats_assessed):
    count = every confirmed chat; scored = valid and not too short;
    too_short = too_short true; could_not_be_read = failed(result);
    from / to = the oldest and newest scored chat's date (None if none scored).
    """
    read = [r for r in results if not failed(r)]
    scored = [r for r in read if not r["too_short"]]
    dates = sorted(r["updated_at"][:10] for r in scored)
    out = {"chats_assessed": {"count": len(results), "scored": len(scored), "too_short": len(read) - len(scored),
                              "could_not_be_read": len(results) - len(read),
                              "from": dates[0] if dates else None, "to": dates[-1] if dates else None}}
    out.update(combine([(r["updated_at"], {cap: r["capabilities"][cap]["level"] for cap in CAPABILITIES})
                        for r in scored]))
    titles = [None if failed(r) or r["too_short"] else
              overall({cap: r["capabilities"][cap]["level"] for cap in CAPABILITIES}, r["agent_session"]["value"])
              for r in results]
    out["chat_titles"] = titles
    out["person"] = person_title([t["level"] for t in titles if t])
    out["proven"] = {cap: reached_in([r["capabilities"][cap]["level"] for r in scored
                                      if r["capabilities"][cap]["level"] != LEVEL_NOT_SHOWN])
                     for cap in CAPABILITIES}
    types = len({r["task_type"] for r in scored})
    used = sum(1 for r in scored if r["reuse"]["value"])
    out["task_range"] = {"types": types, "line": f"Task range: {types} of {len(TASK_TYPES)} types"}
    out["reuse"] = {"chats": used, "line": f"Reused saved work: {used} of {len(scored)} chats"}
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    results = json.loads(pathlib.Path(sys.argv[1]).read_text())
    problems = [f"result {i}: {e}" for i, r in enumerate(results) if not failed(r) for e in validate(r)]
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(json.dumps(aggregate(results), indent=2))
