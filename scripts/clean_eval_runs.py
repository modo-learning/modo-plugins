"""Delete the raw session files the plugin eval runner leaves beside cases.

When a case resumes a history, the runner writes the run's own session next to
the case: plugins/<plugin>/evals/<case>/<uuid>.jsonl and a <uuid>/ folder. They
are raw (not scrubbed) and git-ignored (see plugins/*/evals/.gitignore), so
they only pile up locally. Only names that are a full UUID
(8-4-4-4-12 hex digits) are matched; the .gitignore pattern is looser, but a
delete should not be.

Usage:
    python3 scripts/clean_eval_runs.py              # list what would go (dry run)
    python3 scripts/clean_eval_runs.py --delete     # delete it
    python3 scripts/clean_eval_runs.py <repo root> [--delete]

Stdlib only. Exit status 0.
"""

import pathlib
import re
import shutil
import sys

UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
REPO = pathlib.Path(__file__).resolve().parent.parent


def raw_runs(plugin: pathlib.Path) -> list:
    """Raw run files and folders under one plugin's evals/<case>/."""
    found = []
    for p in sorted((plugin / "evals").glob("*/*")):
        if p.is_dir() and not p.is_symlink() and UUID.match(p.name):
            found.append(p)
        elif p.is_file() and p.suffix == ".jsonl" and UUID.match(p.stem):
            found.append(p)
    return found


def main(argv) -> int:
    delete = "--delete" in argv
    args = [a for a in argv if not a.startswith("--")]
    repo = pathlib.Path(args[0]) if args else REPO
    found = [p for plugin in sorted((repo / "plugins").glob("*")) for p in raw_runs(plugin)]
    for p in found:
        is_dir = p.is_dir()
        if delete:
            shutil.rmtree(p) if is_dir else p.unlink()
        print(("deleted " if delete else "would delete ") + str(p) + ("/" if is_dir else ""))
    if not found:
        print("no raw eval run files found")
    elif not delete:
        print(f"{len(found)} item(s). Dry run: nothing deleted. Re-run with --delete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
