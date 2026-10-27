"""Fail when the copies of a plugin's rubric file differ.

The Modo AI Skills rubric lives in skills/assess-my-ai-work/rubric-v1.md and a
second copy sits in skills/help-me-improve/ so each skill folder is
self-contained (skills docs only document files bundled inside the skill's own
folder). Edit the first, then copy it over the second.

Usage: python3 scripts/check_rubric_sync.py plugins/modo-ai-skills
"""

import pathlib
import sys

NAME = "rubric-v1.md"


def check(plugin: pathlib.Path) -> list:
    copies = sorted((plugin / "skills").glob(f"*/{NAME}"))
    if len(copies) < 2:
        return [f"expected at least 2 copies of {NAME} under {plugin}/skills, found {len(copies)}"]
    first = copies[0].read_bytes()
    return [f"{c} differs from {copies[0]}" for c in copies[1:] if c.read_bytes() != first]


if __name__ == "__main__":
    problems = check(pathlib.Path(sys.argv[1]))
    for p in problems:
        print("FAIL:", p)
    if problems:
        sys.exit(1)
    print("rubric copies identical")
