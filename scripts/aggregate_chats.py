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
  was reached twice (a one-off peak is not a sustained level).
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

Usage:
    python3 -I scripts/aggregate_chats.py results.json   # a JSON list, one entry per chat
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rubric_common import CAPABILITIES, LEVEL_NOT_SHOWN  # noqa: E402
from validate_chat_result import validate  # noqa: E402


# The thresholds. The skill text (assess-my-chats/SKILL.md, step 4), RECORD.md
# and export-assessment/SKILL.md state them in words, since no script runs in
# claude.ai; test_assess_my_chats_skill.py checks the words match these.
BEST_MIN_CHATS = 2      # best_shown: a level reached in at least this many chats
HIGH_MIN_CHATS = 3      # high confidence: shown in at least this many chats ...
CLOSE_SPREAD = 1        # ... with a spread of at most this
MEDIUM_CHATS = 2        # medium: shown in exactly this many chats with a close spread,
MEDIUM_SPREAD = 2       # or in HIGH_MIN_CHATS or more with exactly this spread
TREND_MIN_CHATS = 4     # trend: only when shown in at least this many chats


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
