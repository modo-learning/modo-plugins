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
case listed in EXPECT_SAVE_QUOTES therefore needs such a grader. The sent record must
also be exactly the record the case's history.jsonl last showed the user (the
last ```json block of an assistant reply), and in save-edit-reshows the final
message must show that record again without its fourth quote.

The save cases are run with scripts/run_save_evals.py, which runs these checks
on its own result and fails the run when they fail.

Usage (out.json is the JSON result the suite wrote; how to produce it is in
plugins/modo-ai-skills/skills/export-assessment/RECORD.md):
    python3 scripts/check_eval_records.py out.json
    python3 scripts/check_eval_records.py out.json --cases=export-approved,export-pdf
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate_assessment_record import extract_block, last_json_block, validate  # noqa: E402

# Cases whose final message must contain a valid record.
EXPECT_RECORD = (
    "export-approved", "export-quote-dropped", "export-scores-only",
    "export-no-transcript", "export-not-shown", "export-pdf",
)
EXPECT_EMPTY_EVIDENCE = ("export-scores-only",)

# The Modo connector's save tool, by its bare MCP name. Claude Code shows it
# as mcp__<server>__save_assessment.
SAVE_TOOL = "save_assessment"

# Save cases: each run must send exactly one valid record carrying this many
# quotes. The single source for these counts (the mocks' guards and the
# history recorder read it too).
EXPECT_SAVE_QUOTES = {
    "save-confirmed": 5,
    "save-quote-dropped": 4,
    "save-scores-only": 0,
    "save-rejected": 5,
}

# save-edit-reshows: the user drops a quote by the number they were shown
# (1-based, as in "Drop quote 4 and save it."); the record must come back
# without it, and nothing is sent.
RESHOWN_CASE, DROPPED_QUOTE = "save-edit-reshows", 4

EVALS = pathlib.Path(__file__).resolve().parent.parent / "plugins" / "modo-ai-skills" / "evals"


def is_save(tool):
    return tool == SAVE_TOOL or str(tool).endswith("__" + SAVE_TOOL)


def without_quote(record, number):
    """The record without quote `number` (1-based, as the user saw it numbered)."""
    return dict(record, evidence=[q for i, q in enumerate(record["evidence"], 1) if i != number])


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


def runs(path, names):
    """(case name, "<case> [arm] run n", run) for every run of the named cases."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for case in data.get("cases", []):
        name = case.get("name")
        if name not in names:
            continue
        for arm, arm_runs in case.get("arms", {}).items():
            for i, run in enumerate(arm_runs, 1):
                yield name, f"{name} [{arm}] run {i}", run


def final_text(run):
    for g in run.get("graders", []):
        if g.get("type", "llm") == "llm" and isinstance(g.get("evidence"), str) and g["evidence"]:
            return g["evidence"]
    return None


def check(path, cases=EXPECT_RECORD):
    problems = []
    for name, where, run in runs(path, cases):
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


def run_calls(run):
    """The mock calls recorded for one run, or None if no grader carries them."""
    for g in run.get("graders", []):
        found = mock_calls(g.get("evidence") or "")
        if found:
            return found
    return None


def check_saves(path, expect=EXPECT_SAVE_QUOTES, evals=EVALS):
    problems = []
    for name, where, run in runs(path, expect):
        saves = [c for c in run_calls(run) or [] if is_save(c.get("tool"))]
        if len(saves) != 1:
            problems.append(f"{where}: expected 1 {SAVE_TOOL} call, found {len(saves)}"
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
    before = shown_record(pathlib.Path(evals) / RESHOWN_CASE)
    problems = []
    for _, where, run in runs(path, (RESHOWN_CASE,)):
        if before is None:
            return [f"{RESHOWN_CASE}: no record shown in its history.jsonl"]
        if last_json_block(final_text(run)) != without_quote(before, DROPPED_QUOTE):
            problems.append(f"{where}: the record shown again is not the earlier record"
                            f" without quote {DROPPED_QUOTE}")
    return problems


def check_all(path, cases=None, evals=EVALS):
    """Every check on one result file; `cases` limits them to those names."""
    keep = (lambda names: names) if cases is None else (lambda names: [n for n in names if n in cases])
    problems = check(path, keep(EXPECT_RECORD))
    problems += check_saves(path, {k: EXPECT_SAVE_QUOTES[k] for k in keep(EXPECT_SAVE_QUOTES)}, evals)
    if keep([RESHOWN_CASE]):
        problems += check_reshown(path, evals)
    return problems


def main(argv):
    files = [a for a in argv if not a.startswith("--")]
    if len(files) != 1:
        print(__doc__)
        return 2
    cases = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--cases=")), None)
    problems = check_all(files[0], cases)
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print("all exported and saved records valid")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
