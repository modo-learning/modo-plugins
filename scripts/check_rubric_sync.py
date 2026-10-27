"""Fail when the copies of a plugin's rubric or record files differ.

The Modo AI Skills rubric lives in skills/assess-my-ai-work/rubric-v1.md and a
second copy sits in skills/help-me-improve/ so each skill folder is
self-contained (skills docs only document files bundled inside the skill's own
folder). Edit the first, then copy it over the second.

The assessment record works the same way: RECORD.md and
assessment-record.schema.json live in skills/export-assessment/ and are copied
into every other skill that builds a record (skills/save-to-passport/). Every
skill folder holding RECORD.md must hold both files, identical to the others.

Usage: python3 scripts/check_rubric_sync.py plugins/modo-ai-skills
"""

import pathlib
import sys

NAME = "rubric-v1.md"
RECORD_FILES = ("RECORD.md", "assessment-record.schema.json")


def _same(copies: list) -> list:
    first = copies[0].read_bytes()
    return [f"{c} differs from {copies[0]}" for c in copies[1:] if c.read_bytes() != first]


def check_record(plugin: pathlib.Path) -> list:
    folders = sorted(p.parent for p in (plugin / "skills").glob(f"*/{RECORD_FILES[0]}"))
    problems = []
    for name in RECORD_FILES:
        missing = [f for f in folders if not (f / name).is_file()]
        problems += [f"{f} has {RECORD_FILES[0]} but no {name}" for f in missing]
        copies = [f / name for f in folders if f not in missing]
        if len(copies) > 1:
            problems += _same(copies)
    return problems


def check(plugin: pathlib.Path) -> list:
    copies = sorted((plugin / "skills").glob(f"*/{NAME}"))
    if len(copies) < 2:
        return [f"expected at least 2 copies of {NAME} under {plugin}/skills, found {len(copies)}"]
    return _same(copies) + check_record(plugin)


if __name__ == "__main__":
    problems = check(pathlib.Path(sys.argv[1]))
    for p in problems:
        print("FAIL:", p)
    if problems:
        sys.exit(1)
    print("rubric and record copies identical")
