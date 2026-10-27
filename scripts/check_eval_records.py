"""Validate the exported records found in a plugin eval result file.

Eval graders only see the final message and cannot run Python, so the strict
record check runs here, afterwards, on the saved JSON result.

Where the text comes from: in a result file, each LLM grader entry carries an
"evidence" string, which for graders that look at the last message is that
message. Every export case therefore needs at least one LLM grader with the
default focus (last_message). Checked against a real result file from this
plugin's earlier cases; other grader types carry no text.

It also checks what the save cases sent to the mocked save_assessment tool.
The mock's own `expect:` guards cannot reject unknown fields or count list
items, so the full validator runs here on every recorded call input. An LLM
grader with `focus: mock_calls` carries the calls in its "evidence" string,
one JSON object per call ({"tool", "input", "output", "verdict"}); checked
against real result files of mock probes on Claude Code 2.1.311. Every save
case listed in EXPECT_SAVE therefore needs such a grader. The sent record must
also be exactly the record the case's history.jsonl last showed the user (the
last ```json block of an assistant reply), and in save-edit-reshows the final
message must show that record again without its fourth quote.

Usage (out.json is the JSON result the suite wrote; how to produce it is in
plugins/modo-ai-skills/skills/export-assessment/RECORD.md):
    python3 scripts/check_eval_records.py out.json
    python3 scripts/check_eval_records.py out.json --cases=export-approved,export-pdf
"""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate_assessment_record import extract_block, validate  # noqa: E402

# Cases whose final message must contain a valid record.
EXPECT_RECORD = (
    "export-approved", "export-quote-dropped", "export-scores-only",
    "export-no-transcript", "export-not-shown", "export-pdf",
)
EXPECT_EMPTY_EVIDENCE = ("export-scores-only",)

# Save cases: each run must send exactly one record, valid, with this many quotes.
EXPECT_SAVE = {
    "save-confirmed": 5,
    "save-quote-dropped": 4,
    "save-scores-only": 0,
    "save-rejected": 5,
}
SAVE_TOOL = "save_assessment"
RESHOWN_CASE, DROPPED_INDEX = "save-edit-reshows", 3  # the case prompt drops quote 4
EVALS = pathlib.Path(__file__).resolve().parent.parent / "plugins" / "modo-ai-skills" / "evals"
FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.S)


def last_json_block(text):
    """The last ```json block in a message, parsed, or None. Text may follow it."""
    blocks = FENCE.findall(text or "")
    if not blocks:
        return None
    try:
        return json.loads(blocks[-1])
    except json.JSONDecodeError:
        return None


def shown_record(case_dir):
    """The record the case's history last showed the user, or None."""
    path = pathlib.Path(case_dir) / "history.jsonl"
    if not path.is_file():
        return None
    found = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(raw)
        content = row.get("message", {}).get("content")
        if row.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "text":
                found = last_json_block(block["text"]) or found
    return found


def final_text(run):
    for g in run.get("graders", []):
        if g.get("type", "llm") == "llm" and isinstance(g.get("evidence"), str) and g["evidence"]:
            return g["evidence"]
    return None


def check(path, cases=EXPECT_RECORD):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    problems = []
    for case in data.get("cases", []):
        name = case.get("name")
        if name not in cases:
            continue
        for arm, runs in case.get("arms", {}).items():
            for i, run in enumerate(runs, 1):
                where = f"{name} [{arm}] run {i}"
                text = final_text(run)
                if text is None:
                    problems.append(f"{where}: no final text in the result (add an LLM grader with focus last_message)")
                    continue
                try:
                    record = extract_block(text)
                except ValueError as e:
                    problems.append(f"{where}: {e}")
                    continue
                problems += [f"{where}: {e}" for e in validate(record)]
                if name in EXPECT_EMPTY_EVIDENCE and record.get("evidence") != []:
                    problems.append(f"{where}: evidence must be an empty list")
    return problems


def mock_calls(text):
    """Every {"tool": ..., "input": ...} object in a mock_calls evidence string."""
    calls, decoder, i = [], json.JSONDecoder(), 0
    while (i := text.find('{"tool"', i)) != -1:
        try:
            obj, end = decoder.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        if isinstance(obj, dict) and "input" in obj:
            calls.append(obj)
        i = end
    return calls


def is_save(tool):
    return tool == SAVE_TOOL or str(tool).endswith("__" + SAVE_TOOL)


def run_calls(run):
    """The mock calls recorded for one run, or None if no grader carries them."""
    for g in run.get("graders", []):
        found = mock_calls(g.get("evidence") or "")
        if found:
            return found
    return None


def check_saves(path, expect=EXPECT_SAVE, evals=EVALS):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    problems = []
    for case in data.get("cases", []):
        name = case.get("name")
        if name not in expect:
            continue
        for arm, runs in case.get("arms", {}).items():
            for i, run in enumerate(runs, 1):
                where = f"{name} [{arm}] run {i}"
                saves = [c for c in run_calls(run) or [] if is_save(c.get("tool"))]
                if len(saves) != 1:
                    problems.append(f"{where}: expected 1 save_assessment call, found {len(saves)}"
                                    " (needs an LLM grader with focus mock_calls)")
                    continue
                record = saves[0]["input"]
                problems += [f"{where}: sent record: {e}" for e in validate(record)]
                shown = shown_record(pathlib.Path(evals) / name)
                if shown is None:
                    problems.append(f"{where}: no record shown in {name}/history.jsonl")
                elif record != shown:
                    problems.append(f"{where}: sent record differs from the record shown in the history")
                quotes = record.get("evidence") if isinstance(record, dict) else None
                if isinstance(quotes, list) and len(quotes) != expect[name]:
                    problems.append(f"{where}: sent {len(quotes)} quotes, expected {expect[name]}")
    return problems


def check_reshown(path, evals=EVALS):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    problems = []
    for case in data.get("cases", []):
        if case.get("name") != RESHOWN_CASE:
            continue
        before = shown_record(pathlib.Path(evals) / RESHOWN_CASE)
        if before is None:
            problems.append(f"{RESHOWN_CASE}: no record shown in its history.jsonl")
            continue
        expected = dict(before, evidence=[q for i, q in enumerate(before["evidence"]) if i != DROPPED_INDEX])
        for arm, runs in case.get("arms", {}).items():
            for i, run in enumerate(runs, 1):
                where = f"{RESHOWN_CASE} [{arm}] run {i}"
                after = last_json_block(final_text(run))
                if after != expected:
                    problems.append(f"{where}: the record shown again is not the earlier record without quote 4")
    return problems


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cases = EXPECT_RECORD
    for a in sys.argv[1:]:
        if a.startswith("--cases="):
            cases = tuple(a.split("=", 1)[1].split(","))
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    found = check(args[0], cases)
    filtered = any(a.startswith("--cases=") for a in sys.argv[1:])
    saves = check_saves(args[0], {k: v for k, v in EXPECT_SAVE.items() if k in cases}
                        if filtered else EXPECT_SAVE)
    if not filtered or RESHOWN_CASE in cases:
        saves += check_reshown(args[0])
    for p in found + saves:
        print("FAIL:", p)
    if not found:
        print("all exported records valid")
    if not saves:
        print("all saved records valid")
    found += saves
    sys.exit(1 if found else 0)
