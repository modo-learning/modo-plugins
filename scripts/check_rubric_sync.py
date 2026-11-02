"""Fail when the copies of a plugin's rubric or record files differ.

The Modo AI Skills rubric lives in skills/assess-my-ai-work/rubric-v<version>.md
and copies sit in skills/help-me-improve/ and skills/assess-my-chats/ (which
passes it to every chat agent) so each skill folder is self-contained (skills docs only document files bundled inside the skill's own
folder). Edit the first, then copy it over the second. The copies must have
the same file name (the same version) and the same bytes.

The assessment record works the same way: RECORD.md and
assessment-record.schema.json live in skills/export-assessment/ and are copied
into every other skill that builds a record (skills/save-to-passport/). Every
skill folder holding RECORD.md must hold both files, identical to the others.

The passport card works the same way: passport-card.html lives in
skills/assess-my-ai-work/ (the source: edit there) and is copied into
skills/assess-my-chats/, which renders a multi-chat result with it. Every copy
must be identical.

Usage: python3 scripts/check_rubric_sync.py plugins/modo-ai-skills
"""

import pathlib
import sys

PATTERN = "rubric-v*.md"
RECORD_FILES = ("RECORD.md", "assessment-record.schema.json")
CARD = "passport-card.html"


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
    copies = sorted((plugin / "skills").glob(f"*/{PATTERN}"))
    if len(copies) < 2:
        return [f"expected at least 2 copies of {PATTERN} under {plugin}/skills, found {len(copies)}"]
    first = copies[0]
    names = [f"{c} differs from {first}" for c in copies[1:] if c.name != first.name]
    cards = sorted((plugin / "skills").glob(f"*/{CARD}"))
    return names + _same(copies) + check_record(plugin) + (_same(cards) if len(cards) > 1 else [])


if __name__ == "__main__":
    problems = check(pathlib.Path(sys.argv[1]))
    for p in problems:
        print("FAIL:", p)
    if problems:
        sys.exit(1)
    print("rubric, record and card copies identical")
