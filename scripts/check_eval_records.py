"""Validate the exported records found in a plugin eval result file.

Eval graders only see the final message and cannot run Python, so the strict
record check runs here, afterwards, on the saved JSON result.

Where the text comes from: in a result file, each LLM grader entry carries an
"evidence" string, which for graders that look at the last message is that
message. Every export case therefore needs at least one LLM grader with the
default focus (last_message). Checked against a real result file from this
plugin's earlier cases; other grader types carry no text.

Usage (out.json is the JSON result the suite wrote; how to produce it is in
plugins/modo-ai-skills/skills/export-assessment/RECORD.md):
    python3 scripts/check_eval_records.py out.json
    python3 scripts/check_eval_records.py out.json --cases=export-approved,export-pdf
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate_assessment_record import extract_block, validate  # noqa: E402

# Cases whose final message must contain a valid record.
EXPECT_RECORD = (
    "export-approved", "export-quote-dropped", "export-scores-only",
    "export-no-transcript", "export-not-shown", "export-pdf",
)
EXPECT_EMPTY_EVIDENCE = ("export-scores-only",)


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
    for p in found:
        print("FAIL:", p)
    if not found:
        print("all exported records valid")
    sys.exit(1 if found else 0)
