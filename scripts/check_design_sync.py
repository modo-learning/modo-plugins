"""Fail when a template's copy of the Modo design tokens differs from the source.

The tokens live in skills/modo-design/modo-tokens.css between the
MODO-TOKENS-START and MODO-TOKENS-END markers. Every HTML template under
skills/ that has those markers carries a copy of the block so each skill folder
is self-contained (the card and the report make no network requests). Edit the
source, then copy the block into each template. The copies must match byte for
byte.

Usage: python3 scripts/check_design_sync.py plugins/modo-ai-skills
"""

import pathlib
import re
import sys

SOURCE = "skills/modo-design/modo-tokens.css"
BLOCK = re.compile(r"/\* MODO-TOKENS-START \*/.*?/\* MODO-TOKENS-END \*/", re.S)


def block(text: str):
    found = BLOCK.findall(text)
    return found[0] if len(found) == 1 else None


def check(plugin: pathlib.Path) -> list:
    source = plugin / SOURCE
    if not source.exists():
        return [f"missing {source}"]
    want = block(source.read_text())
    if want is None:
        return [f"{source} must hold exactly one marked token block"]
    templates = sorted(p for p in (plugin / "skills").glob("*/*.html") if "MODO-TOKENS" in p.read_text())
    if not templates:
        return [f"no template under {plugin}/skills carries the token block"]
    problems = []
    for t in templates:
        got = block(t.read_text())
        if got is None:
            problems.append(f"{t} must hold exactly one marked token block")
        elif got != want:
            problems.append(f"{t} token block differs from {source}")
    return problems


if __name__ == "__main__":
    problems = check(pathlib.Path(sys.argv[1]))
    for p in problems:
        print("FAIL:", p)
    if problems:
        sys.exit(1)
    print("design tokens identical")
