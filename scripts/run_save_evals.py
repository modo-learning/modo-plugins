"""Run the modo-ai-skills save cases and the strict record check on their result.

This is the way to run the save evals. `claude plugin eval` alone cannot fail
a run on what was sent to the mocked save_assessment tool: the mock's
`expect:` guards cannot reject an unknown field or count list items, and LLM
graders are judgements. So for each case this runs the eval, then runs the
checks of scripts/check_eval_records.py on the result it wrote (exactly one
valid save call with the expected number of quotes, equal to the record the
history showed; for save-edit-reshows, the record shown again without the
dropped quote). It exits 1 if any eval or any check fails.

Usage (from the repo root):
    python3 scripts/run_save_evals.py                       # every save case
    python3 scripts/run_save_evals.py --runs 2 save-confirmed save-declined
    python3 scripts/run_save_evals.py save-rejected -- --judge-model sonnet

--runs N overrides the cases' runs; --output-dir DIR is where each case's
aggregate-result.json goes (DIR/<case>/; default
plugins/modo-ai-skills/evals/results/save-<timestamp>/). Anything after `--`
is passed to `claude plugin eval` as is. Every eval runs with
`--ablation none --no-publish`.
"""

import datetime
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_eval_records import EVALS, check_all  # noqa: E402
from gen_ai_skills_eval_history import CONNECTOR_CASES  # noqa: E402

PLUGIN = EVALS.parent
SAVE_CASES = (*CONNECTOR_CASES, "save-no-connector", "save-not-offered")


def parse(argv):
    argv, extra = (argv[:argv.index("--")], argv[argv.index("--") + 1:]) if "--" in argv else (argv, [])
    runs, out, cases, i = None, None, [], 0
    while i < len(argv):
        if argv[i] in ("--runs", "--output-dir"):
            if argv[i] == "--runs":
                runs = argv[i + 1]
            else:
                out = pathlib.Path(argv[i + 1])
            i += 2
        else:
            cases.append(argv[i])
            i += 1
    if out is None:
        out = EVALS / "results" / ("save-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    return runs, out, cases or list(SAVE_CASES), extra


def run_case(case, runs, out, extra, run):
    """Problems for one case: a failed eval, a missing result, failed record checks."""
    cmd = ["claude", "plugin", "eval", str(PLUGIN), "--case", case, "--output-dir", str(out),
           "--ablation", "none", "--no-publish"] + (["--runs", runs] if runs else []) + extra
    code = run(cmd).returncode
    problems = [f"{case}: claude plugin eval exited {code}"] if code else []
    result = out / "aggregate-result.json"
    if not result.is_file():
        return problems + [f"{case}: no result at {result}"]
    return problems + check_all(result, [case])


def main(argv, run=subprocess.run):
    runs, out, cases, extra = parse(argv)
    unknown = [c for c in cases if c not in SAVE_CASES]
    if unknown:
        print(__doc__)
        print("not a save case:", ", ".join(unknown))
        return 2
    problems = []
    for case in cases:
        found = run_case(case, runs, out / case, extra, run)
        print(f"{case}: {'FAIL' if found else 'pass'} ({out / case / 'aggregate-result.json'})")
        problems += found
    for p in problems:
        print("FAIL:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
