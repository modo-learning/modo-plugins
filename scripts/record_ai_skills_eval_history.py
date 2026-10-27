"""Record the real first turns used by the modo-ai-skills decline cases.

improve-decline resumes a conversation in which assess-my-ai-work has already
assessed the planted pricing chat; export-decline resumes one in which
export-assessment has also shown its export plan. Hand-written turns don't
work for these: they lack the skill load and the rubric read, and the model
notices. So this script seeds the planted chat (from the
strong-verify-weak-delegate history) as a session, resumes it headless with the
plugin, and keeps what really happened. Re-run it after every change to the
skills.

Cleaning follows scripts/record_eval_history.py: only user and assistant rows,
local paths replaced, and it refuses to write if home paths or e-mail
addresses remain.

Usage (from the repo root): python3 scripts/record_ai_skills_eval_history.py
"""

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "modo-ai-skills"
EVALS = PLUGIN / "evals"
SEED = EVALS / "strong-verify-weak-delegate"
EXPORT_REQUEST = "Export this as a report."
DROP_KEYS = ("gitBranch", "slug", "userType", "entrypoint", "version", "requestId")
LEAK = re.compile(r"/Users/|/home/|[\w.+-]+@[\w-]+\.[\w.]+")


def seed(workdir: pathlib.Path) -> tuple[str, pathlib.Path]:
    """Write the planted chat as a session Claude Code can resume."""
    session = str(uuid.uuid4())
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(workdir))
    path = pathlib.Path.home() / ".claude" / "projects" / slug / f"{session}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for raw in (SEED / "history.jsonl").read_text().splitlines():
        msg = json.loads(raw)
        msg["sessionId"], msg["cwd"] = session, str(workdir)
        rows.append(json.dumps(msg))
    path.write_text("\n".join(rows) + "\n")
    return session, path


def resume(session: str, prompt: str, workdir: pathlib.Path) -> None:
    subprocess.run(
        ["claude", "-p", "--resume", session, "--plugin-dir", str(PLUGIN),
         "--allowedTools", "Read,Glob,Grep,Skill"],
        input=prompt, text=True, cwd=workdir, check=True, capture_output=True,
    )


def clean(src: pathlib.Path, workdir: pathlib.Path) -> str:
    lines, prev = [], None
    for raw in src.read_text().splitlines():
        msg = json.loads(raw)
        if msg.get("type") not in ("user", "assistant"):
            continue
        msg["parentUuid"], prev = prev, msg["uuid"]
        for key in DROP_KEYS:
            msg.pop(key, None)
        text = json.dumps(msg, ensure_ascii=False)
        text = text.replace(str(workdir), "/workspace")
        text = text.replace(str(PLUGIN), "/plugin")
        lines.append(text)
    out = "\n".join(lines) + "\n"
    leak = LEAK.search(out)
    if leak:
        sys.exit(f"cleaned transcript still contains {leak.group(0)!r}; not writing")
    return out


def last_text(history: str) -> str:
    for raw in reversed(history.splitlines()):
        msg = json.loads(raw)
        content = msg["message"].get("content")
        if msg["type"] == "assistant" and isinstance(content, list):
            texts = [b["text"] for b in content if b.get("type") == "text"]
            if texts:
                return texts[-1]
    return ""


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp).resolve()
        session, path = seed(workdir)
        try:
            resume(session, (SEED / "prompt.md").read_text(), workdir)
            assessed = clean(path, workdir)
            if "Improvements" not in last_text(assessed):
                sys.exit("recorded assessment has no Improvements section; not writing")
            resume(session, EXPORT_REQUEST, workdir)
            planned = clean(path, workdir)
            if '"session_date"' in last_text(planned) or "Export plan" not in last_text(planned):
                sys.exit("recorded export turn is not an export plan; not writing")
        finally:
            path.unlink(missing_ok=True)
            try:
                path.parent.rmdir()
            except OSError:
                pass
    (EVALS / "improve-decline" / "history.jsonl").write_text(assessed)
    (EVALS / "export-decline" / "history.jsonl").write_text(planned)
    print("wrote history.jsonl to improve-decline, export-decline")


if __name__ == "__main__":
    main()
