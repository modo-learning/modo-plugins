"""Combine per-chat results into one multi-chat assessment (stdlib only).

PROPOSED RULES, pending product sign-off. The rules are arithmetic on purpose:
the same chat results always give the same combined result, and the model
never "averages by feel".

Input: a list of ChatResults (see validate_chat_result.py), each already valid.
A chat that is too short is listed but scores nothing.

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
    python3 -I scripts/aggregate_chats.py results.json   # a JSON list of ChatResults
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rubric_common import CAPABILITIES, LEVEL_NOT_SHOWN  # noqa: E402
from validate_chat_result import validate  # noqa: E402


def lower_median(values):
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


def combined_confidence(levels):
    n, spread = len(levels), max(levels) - min(levels)
    if n >= 3 and spread <= 1:
        return "high"
    if (n == 2 and spread <= 1) or (n >= 3 and spread == 2):
        return "medium"
    return "low"


def best_shown(levels):
    repeated = [lvl for lvl in set(levels) if levels.count(lvl) >= 2]
    return max(repeated) if repeated else None


def trend(dated):
    if len(dated) < 4:
        return None
    levels = [lvl for _, lvl in sorted(dated, key=lambda d: d[0])]
    half = len(levels) // 2
    earlier, later = lower_median(levels[:half]), lower_median(levels[-half:])
    return "up" if later > earlier else "down" if later < earlier else "flat"


def aggregate(results):
    scored = [r for r in results if not r["too_short"]]
    capabilities = {}
    for cap in CAPABILITIES:
        dated = [(r["updated_at"], r["capabilities"][cap]["level"]) for r in scored
                 if r["capabilities"][cap]["level"] != LEVEL_NOT_SHOWN]
        levels = [lvl for _, lvl in dated]
        if not levels:
            capabilities[cap] = {"level": LEVEL_NOT_SHOWN, "confidence": "low", "best_shown": None,
                                 "trend": None, "chats_shown": 0}
            continue
        capabilities[cap] = {"level": lower_median(levels), "confidence": combined_confidence(levels),
                             "best_shown": best_shown(levels), "trend": trend(dated),
                             "chats_shown": len(levels)}
    dates = sorted(r["updated_at"][:10] for r in scored)
    return {
        "chats_listed": len(results),
        "chats_scored": len(scored),
        "chats_too_short": len(results) - len(scored),
        "date_range": [dates[0], dates[-1]] if dates else None,
        "coverage": sum(1 for c in capabilities.values() if c["level"] != LEVEL_NOT_SHOWN),
        "capabilities": capabilities,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    results = json.loads(pathlib.Path(sys.argv[1]).read_text())
    problems = [f"result {i}: {e}" for i, r in enumerate(results) for e in validate(r)]
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(json.dumps(aggregate(results), indent=2))
