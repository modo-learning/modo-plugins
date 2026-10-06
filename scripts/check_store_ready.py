"""Check a plugin folder against the blocking rules in Anthropic's plugin
pre-submission checklist that can be checked locally.

Source: https://claude.com/docs/plugins/pre-submission-checklist
This does not replace the developer portal's Validate button; run that too
before submitting.

Usage: python3 scripts/check_store_ready.py plugins/modo-task-finder
"""

import json
import pathlib
import re
import subprocess
import sys

JUNK = {".DS_Store", "Thumbs.db", "desktop.ini", "__MACOSX"}
NAME = re.compile(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")
RESERVED = {"claude", "anthropic", "official", "plugin", "mcp", "test"}
SECRET = re.compile(r"(sk-ant-|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})")
IMAGE_OR_FONT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".woff", ".woff2", ".ttf", ".otf"}


def readme_words(text: str) -> int:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.findall(r"\b\w+\b", text))


def main(folder: str) -> None:
    root = pathlib.Path(folder)
    problems, holds = [], []
    files = [p for p in root.rglob("*") if ".git" not in p.parts]

    manifest = root / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        problems.append("missing .claude-plugin/plugin.json")
    else:
        data = json.loads(manifest.read_text())
        name = data.get("name", "")
        if not NAME.match(name):
            problems.append(f"name {name!r} is not lowercase letters, digits and hyphens")
        if name in RESERVED:
            problems.append(f"name {name!r} is reserved")
        for key in ("description", "author", "version"):
            if key not in data:
                holds.append(f"plugin.json has no {key} (warning)")
        if "license" not in data and not (root / "LICENSE").is_file():
            problems.append("no LICENSE file and no license in plugin.json")

    readme = root / "README.md"
    if not readme.is_file():
        problems.append("missing README.md")
    elif readme_words(readme.read_text()) < 40:
        problems.append("README has fewer than 40 words outside code blocks")

    names_lower = {}
    for p in files:
        if p.name in JUNK or any(part in JUNK for part in p.parts):
            problems.append(f"system file: {p}")
        if p.is_symlink():
            problems.append(f"symlink: {p}")
        if re.search(r'[:]|[. ]$', p.name):
            problems.append(f"file name not valid on Windows: {p}")
        key = str(p).lower()
        if key in names_lower:
            problems.append(f"names differ only by case: {p} / {names_lower[key]}")
        names_lower[key] = p
        if p.is_file():
            size = p.stat().st_size
            if size > 5 * 1024 * 1024:
                problems.append(f"file over 5 MiB: {p}")
            elif size > 256 * 1024 and p.suffix.lower() not in IMAGE_OR_FONT:
                holds.append(f"file over 256 KiB, held for review: {p}")
            try:
                text = p.read_text()
            except UnicodeDecodeError:
                if p.suffix.lower() not in IMAGE_OR_FONT:
                    holds.append(f"binary file, held for review: {p}")
                continue
            if SECRET.search(text):
                problems.append(f"possible credential in {p}")
    file_count = sum(1 for p in files if p.is_file())
    if file_count > 512:
        holds.append(f"{file_count} files (over 512), held for review")

    result = subprocess.run(["claude", "plugin", "validate", str(root)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        problems.append("claude plugin validate failed:\n" + result.stdout + result.stderr)

    for h in holds:
        print("HOLD/WARN:", h)
    for p in problems:
        print("BLOCKING:", p)
    print(f"{file_count} files checked. "
          + ("No blocking problems found." if not problems else f"{len(problems)} blocking problem(s)."))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "plugins/modo-task-finder")
