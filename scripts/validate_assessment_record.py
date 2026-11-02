"""Validate a Modo AI Skills assessment record (stdlib only).

The record shape is specified in
plugins/modo-ai-skills/skills/export-assessment/RECORD.md (source: the
"Assessment record" section of SPEC-modo-ai-skills.md).

Usage:
    python3 scripts/validate_assessment_record.py report.md        # last json block
    python3 scripts/validate_assessment_record.py record.json      # bare JSON
    python3 scripts/validate_assessment_record.py report.md --spec-only

Exit status 0 when valid, 1 otherwise. Errors are printed one per line.

`--spec-only` checks only the rules in the spec. Without it the two plugin
conventions in RECORD.md are also enforced: a not_shown capability records
confidence "low", and no quote is attached to a not_shown capability.
"""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from aggregate_chats import best_shown, combined_confidence, lower_median, trend  # noqa: E402
from rubric_common import (CAPABILITIES, CONFIDENCE, LEVEL_NOT_SHOWN, MAX_QUOTE,  # noqa: E402
                           is_date as _is_date, is_int as _is_int, is_level as _is_level)

LABEL = "Self-assessment by Claude using Modo rubric v1.1 — not verified."

MAX_EVIDENCE = 5
MAX_TITLE = 120
TOP_FIELDS = {"rubric_version", "capabilities", "evidence", "session_title", "session_date"}
MULTI_CHAT = "multi_chat"
MULTI_TOP_FIELDS = TOP_FIELDS | {"scope", "chats_assessed", "chats", "coverage"}
MULTI_CAP_FIELDS = {"level", "confidence", "best_shown", "trend", "chats_shown"}
ASSESSED_FIELDS = {"count", "scored", "too_short", "could_not_be_read", "from", "to"}
CHAT_FIELDS = {"title", "date", "result", "levels"}
CHAT_RESULTS = ("scored", "too_short", "could_not_be_read")
TRENDS = ("up", "flat", "down", None)
MAX_CHATS = 25

VERSION = re.compile(r"^v[0-9]+(\.[0-9]+)?$")
FENCE = re.compile(r"^```json[ \t]*\n(.*?)\n```[ \t]*$", re.M | re.S)


def _is_str(v):
    return isinstance(v, str)


def _fields(obj, allowed, where, errors, required=True):
    extra = sorted(set(obj) - set(allowed))
    if extra:
        errors.append(f"{where}: unknown field(s) {extra}")
    missing = sorted(set(allowed) - set(obj)) if required else []
    if missing:
        errors.append(f"{where}: missing field(s) {missing}")


def _title(t, where, errors):
    if not _is_str(t) or not t.strip():
        errors.append(f"{where}: must be a non-empty string")
    elif len(t) > MAX_TITLE:
        errors.append(f"{where}: {len(t)} characters, limit {MAX_TITLE}")


def validate(record, convention=True):
    """Return a list of error strings; empty means valid."""
    if not isinstance(record, dict):
        return ["record: must be a JSON object"]
    errors = []
    is_multi = "scope" in record
    _fields(record, MULTI_TOP_FIELDS if is_multi else TOP_FIELDS, "record", errors)
    if is_multi and record["scope"] != MULTI_CHAT:
        errors.append(f"scope: must be '{MULTI_CHAT}' (leave it out for a single chat)")

    v = record.get("rubric_version")
    if "rubric_version" in record and not (_is_str(v) and VERSION.match(v)):
        errors.append("rubric_version: must be a string like 'v1' or 'v1.1'")

    caps = record.get("capabilities")
    shown = {}
    cap_fields = MULTI_CAP_FIELDS if is_multi else {"level", "confidence"}
    if "capabilities" in record:
        if not isinstance(caps, dict):
            errors.append("capabilities: must be an object")
        else:
            _fields(caps, CAPABILITIES, "capabilities", errors)
            for name in CAPABILITIES:
                entry = caps.get(name)
                if entry is None:
                    continue
                where = f"capabilities.{name}"
                if not isinstance(entry, dict):
                    errors.append(f"{where}: must be an object")
                    continue
                _fields(entry, cap_fields, where, errors)
                level, conf = entry.get("level"), entry.get("confidence")
                if "level" in entry and not _is_level(level):
                    errors.append(f"{where}.level: must be an integer 1-5 or 'not_shown'")
                if "confidence" in entry and conf not in CONFIDENCE:
                    errors.append(f"{where}.confidence: must be one of {list(CONFIDENCE)}")
                shown[name] = level != LEVEL_NOT_SHOWN
                if convention and level == LEVEL_NOT_SHOWN and conf != "low":
                    errors.append(f"{where}.confidence: convention: a not_shown capability records 'low'")

    ev = record.get("evidence")
    ev_fields = {"capability", "quote", "chat"} if is_multi else {"capability", "quote"}
    if "evidence" in record:
        if not isinstance(ev, list):
            errors.append("evidence: must be a list")
        else:
            if len(ev) > MAX_EVIDENCE:
                errors.append(f"evidence: at most {MAX_EVIDENCE} items, got {len(ev)}")
            for i, item in enumerate(ev):
                where = f"evidence[{i}]"
                if not isinstance(item, dict):
                    errors.append(f"{where}: must be an object")
                    continue
                _fields(item, ev_fields, where, errors)
                cap, quote = item.get("capability"), item.get("quote")
                if "capability" in item and cap not in CAPABILITIES:
                    errors.append(f"{where}.capability: must be one of {list(CAPABILITIES)}")
                elif convention and shown.get(cap) is False:
                    errors.append(f"{where}.capability: convention: no quote for a not_shown capability")
                if "quote" in item:
                    if not _is_str(quote) or not quote.strip():
                        errors.append(f"{where}.quote: must be a non-empty string")
                    elif len(quote) > MAX_QUOTE:
                        errors.append(f"{where}.quote: {len(quote)} characters, limit {MAX_QUOTE}")

    if "session_title" in record:
        _title(record["session_title"], "session_title", errors)

    if "session_date" in record and not _is_date(record["session_date"]):
        errors.append("session_date: must be a real calendar date, yyyy-mm-dd")

    if is_multi and not errors:
        _validate_multi(record, convention, errors)
    return errors


def _validate_chats(chats, errors):
    """Per-chat summaries: shape only. Returns True when every entry is well formed."""
    if not isinstance(chats, list) or not chats:
        errors.append("chats: must be a non-empty list")
        return False
    if len(chats) > MAX_CHATS:
        errors.append(f"chats: at most {MAX_CHATS} items, got {len(chats)}")
    start = len(errors)
    for i, chat in enumerate(chats):
        where = f"chats[{i}]"
        if not isinstance(chat, dict):
            errors.append(f"{where}: must be an object")
            continue
        _fields(chat, CHAT_FIELDS, where, errors)
        if "title" in chat:
            _title(chat["title"], f"{where}.title", errors)
        if "date" in chat and not _is_date(chat["date"]):
            errors.append(f"{where}.date: must be a real calendar date, yyyy-mm-dd")
        result, levels = chat.get("result"), chat.get("levels")
        if result not in CHAT_RESULTS:
            errors.append(f"{where}.result: must be one of {list(CHAT_RESULTS)}")
        elif result == "scored":
            if not isinstance(levels, dict):
                errors.append(f"{where}.levels: a scored chat gives the five levels")
            else:
                _fields(levels, CAPABILITIES, f"{where}.levels", errors)
                for name in CAPABILITIES:
                    if name in levels and not _is_level(levels[name]):
                        errors.append(f"{where}.levels.{name}: must be an integer 1-5 or 'not_shown'")
        elif levels is not None:
            errors.append(f"{where}.levels: must be null for a chat that was not scored")
    return len(errors) == start


def _validate_multi(record, convention, errors):
    """Rules that tie a multi-chat record together; run only once every field is well formed."""
    chats = record["chats"]
    if not _validate_chats(chats, errors):
        return
    dates = [c["date"] for c in chats]
    if dates != sorted(dates, reverse=True):
        errors.append("chats: must be newest first")
    scored = [(i + 1, c) for i, c in enumerate(chats) if c["result"] == "scored"]

    summary = record["chats_assessed"]
    if not isinstance(summary, dict):
        errors.append("chats_assessed: must be an object")
    else:
        _fields(summary, ASSESSED_FIELDS, "chats_assessed", errors)
        for key in ("count", "scored", "too_short", "could_not_be_read"):
            if key in summary and not (_is_int(summary[key]) and summary[key] >= 0):
                errors.append(f"chats_assessed.{key}: must be a whole number, 0 or more")
        for key in ("from", "to"):
            if key in summary and not _is_date(summary[key]):
                errors.append(f"chats_assessed.{key}: must be a real calendar date, yyyy-mm-dd")
        if not errors:
            want = {"count": len(chats)}
            want.update({r: sum(1 for c in chats if c["result"] == r) for r in CHAT_RESULTS})
            for key, n in want.items():
                if summary[key] != n:
                    errors.append(f"chats_assessed.{key}: is {summary[key]}, the chats list gives {n}")
            if not scored:
                errors.append("chats: at least one chat must be scored")
            else:
                first, last = min(c["date"] for _, c in scored), max(c["date"] for _, c in scored)
                if (summary["from"], summary["to"]) != (first, last):
                    errors.append(f"chats_assessed: from/to must be the scored chats' dates, {first} to {last}")
                if record["session_date"] != last:
                    errors.append(f"session_date: must be the newest scored chat's date, {last}")
    if errors:
        return

    # Recompute the combined levels with the same arithmetic as aggregate_chats.py.
    oldest_first = [c for _, c in reversed(scored)]
    shown_count = 0
    for name in CAPABILITIES:
        entry = record["capabilities"][name]
        where = f"capabilities.{name}"
        if entry["best_shown"] is not None and not (_is_int(entry["best_shown"]) and 1 <= entry["best_shown"] <= 5):
            errors.append(f"{where}.best_shown: must be an integer 1-5 or null")
        if entry["trend"] not in TRENDS:
            errors.append(f"{where}.trend: must be 'up', 'flat', 'down' or null")
        if not (_is_int(entry["chats_shown"]) and entry["chats_shown"] >= 0):
            errors.append(f"{where}.chats_shown: must be a whole number, 0 or more")
        dated = [(i, c["levels"][name]) for i, c in enumerate(oldest_first) if c["levels"][name] != LEVEL_NOT_SHOWN]
        levels = [lvl for _, lvl in dated]
        if levels:
            shown_count += 1
            want = {"level": lower_median(levels), "confidence": combined_confidence(levels),
                    "best_shown": best_shown(levels), "trend": trend(dated), "chats_shown": len(levels)}
        else:
            want = {"level": "not_shown", "confidence": "low", "best_shown": None, "trend": None, "chats_shown": 0}
        for key, value in want.items():
            if entry[key] != value:
                errors.append(f"{where}.{key}: is {entry[key]!r}, the per-chat levels give {value!r}")

    coverage = record["coverage"]
    if coverage != shown_count or not _is_int(coverage):
        errors.append(f"coverage: must be {shown_count}, the number of capabilities shown in a scored chat")

    for i, item in enumerate(record["evidence"]):
        where, n = f"evidence[{i}].chat", item["chat"]
        if not (_is_int(n) and 1 <= n <= len(chats)):
            errors.append(f"{where}: must be a chat number from 1 to {len(chats)}")
            continue
        chat = chats[n - 1]
        if chat["result"] != "scored" or chat["levels"][item["capability"]] == LEVEL_NOT_SHOWN:
            errors.append(f"{where}: chat {n} must be scored and show {item['capability']}")
        elif convention and chat["levels"][item["capability"]] != record["capabilities"][item["capability"]]["level"]:
            errors.append(f"{where}: convention: quote from a chat whose level equals the combined level")


def last_json_block(text):
    """The last ```json block in a message, parsed, or None.

    Unlike extract_block, any text may follow the block (a chat reply that
    shows a record and then asks a question)."""
    matches = list(FENCE.finditer(text or ""))
    if not matches:
        return None
    try:
        return json.loads(matches[-1].group(1))
    except json.JSONDecodeError:
        return None


def extract_block(text):
    """Return the record from the last ```json fence in a report.

    Only whitespace, or the result label, may follow the closing fence.
    Raises ValueError when there is no block, trailing text or bad JSON.
    """
    matches = list(FENCE.finditer(text))
    if not matches:
        raise ValueError("no ```json block found")
    last = matches[-1]
    tail = text[last.end():].strip()
    if tail not in ("", LABEL):
        raise ValueError("text after the final json block (only the result label may follow)")
    try:
        return json.loads(last.group(1))
    except json.JSONDecodeError as e:
        raise ValueError(f"block is not valid JSON: {e}")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    text = pathlib.Path(args[0]).read_text(encoding="utf-8")
    try:
        record = json.loads(text) if args[0].endswith(".json") else extract_block(text)
    except ValueError as e:
        print("FAIL:", e)
        return 1
    errors = validate(record, convention="--spec-only" not in argv)
    for e in errors:
        print("FAIL:", e)
    if not errors:
        print("valid assessment record")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
