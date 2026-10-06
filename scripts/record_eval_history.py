"""Record the first /my-tasks turn used by the follow-up eval cases.

The build-skill, build-scheduled and decline cases resume a conversation in
which /my-tasks has already listed the planted-patterns tasks. That first
turn replays the skill text as it was when recorded, so re-run this script
after every change to the skill.

It runs one real headless session on the planted export, keeps only the
user and assistant messages, replaces local paths, drops lines about
connectors the recording machine happens to have, and writes the
result into each follow-up case as history.jsonl. It refuses to write if
the cleaned transcript still contains home paths or e-mail addresses.

Usage (from the repo root): python3 scripts/record_eval_history.py
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "modo-task-finder"
PLANTED = PLUGIN / "evals" / "planted-patterns"
FOLLOW_UPS = ["build-skill", "build-scheduled", "decline"]
DROP_KEYS = ("gitBranch", "slug", "userType", "entrypoint", "version", "requestId")
MACHINE_NOTE = re.compile(r"re-?authori[sz]|connector settings|Notion", re.I)
LEAK = re.compile(r"/Users/|/home/|[\w.+-]+@[\w-]+\.[\w.]+")


def record(workdir: pathlib.Path) -> pathlib.Path:
    (workdir / "resources").mkdir()
    shutil.copy(PLANTED / "resources" / "conversations.json", workdir / "resources")
    session = str(uuid.uuid4())
    prompt = (PLANTED / "prompt.md").read_text()
    subprocess.run(
        ["claude", "-p", "--session-id", session,
         "--plugin-dir", str(PLUGIN),
         "--plugin-dir", str(PLANTED / "fixture-plugins" / "investor-update"),
         "--allowedTools", "Read,Glob,Grep,Skill"],
        input=prompt, text=True, cwd=workdir, check=True, capture_output=True,
    )
    matches = list(pathlib.Path.home().glob(f".claude/projects/*/{session}.jsonl"))
    if not matches:
        sys.exit("recorded session transcript not found")
    return matches[0]


def clean(src: pathlib.Path, workdir: pathlib.Path) -> str:
    lines, prev = [], None
    for raw in src.read_text().splitlines():
        msg = json.loads(raw)
        if msg.get("type") not in ("user", "assistant"):
            continue
        content = msg["message"].get("content")
        if msg["type"] == "assistant" and isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    block["text"] = "\n".join(
                        p for p in block["text"].split("\n")
                        if not MACHINE_NOTE.search(p))
        msg["parentUuid"], prev = prev, msg["uuid"]
        for key in DROP_KEYS:
            msg.pop(key, None)
        text = json.dumps(msg, ensure_ascii=False)
        text = text.replace(str(workdir.resolve()), "/workspace")
        text = text.replace(str(workdir), "/workspace")
        text = text.replace(str(PLUGIN), "/plugin")
        lines.append(text)
    out = "\n".join(lines) + "\n"
    leak = LEAK.search(out)
    if leak:
        sys.exit(f"cleaned transcript still contains {leak.group(0)!r}; not writing")
    return out


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        src = record(workdir)
        try:
            history = clean(src, workdir)
        finally:
            src.unlink()
    for case in FOLLOW_UPS:
        (PLUGIN / "evals" / case / "history.jsonl").write_text(history)
    print(f"wrote history.jsonl to {', '.join(FOLLOW_UPS)}")


if __name__ == "__main__":
    main()
