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

import datetime
import json
import pathlib
import re
import sys

LABEL = "Self-assessment by Claude using Modo rubric v1 — not verified."

CAPABILITIES = ("problem_solving", "verification", "workflow_design", "delegation", "strategic_thinking")
CONFIDENCE = ("low", "medium", "high")
MAX_EVIDENCE = 5
MAX_QUOTE = 240
MAX_TITLE = 120
TOP_FIELDS = {"rubric_version", "capabilities", "evidence", "session_title", "session_date"}

VERSION = re.compile(r"^v[0-9]+$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
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


def validate(record, convention=True):
    """Return a list of error strings; empty means valid."""
    if not isinstance(record, dict):
        return ["record: must be a JSON object"]
    errors = []
    _fields(record, TOP_FIELDS, "record", errors)

    v = record.get("rubric_version")
    if "rubric_version" in record and not (_is_str(v) and VERSION.match(v)):
        errors.append("rubric_version: must be a string like 'v1'")

    caps = record.get("capabilities")
    shown = {}
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
                _fields(entry, {"level", "confidence"}, where, errors)
                level, conf = entry.get("level"), entry.get("confidence")
                ok_level = level == "not_shown" or (
                    isinstance(level, int) and not isinstance(level, bool) and 1 <= level <= 5
                )
                if "level" in entry and not ok_level:
                    errors.append(f"{where}.level: must be an integer 1-5 or 'not_shown'")
                if "confidence" in entry and conf not in CONFIDENCE:
                    errors.append(f"{where}.confidence: must be one of {list(CONFIDENCE)}")
                shown[name] = level != "not_shown"
                if convention and level == "not_shown" and conf != "low":
                    errors.append(f"{where}.confidence: convention: a not_shown capability records 'low'")

    ev = record.get("evidence")
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
                _fields(item, {"capability", "quote"}, where, errors)
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
        t = record["session_title"]
        if not _is_str(t) or not t.strip():
            errors.append("session_title: must be a non-empty string")
        elif len(t) > MAX_TITLE:
            errors.append(f"session_title: {len(t)} characters, limit {MAX_TITLE}")

    if "session_date" in record:
        d = record["session_date"]
        ok = False
        if _is_str(d) and DATE.match(d):
            try:
                datetime.date.fromisoformat(d)
                ok = True
            except ValueError:
                pass
        if not ok:
            errors.append("session_date: must be a real calendar date, yyyy-mm-dd")
    return errors


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
