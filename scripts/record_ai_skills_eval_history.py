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

The save cases (ticket 10) are recorded the same way, but with the Modo
connector present: pass an MCP config file for a local modo-mcp server named
"modo" (how to run one: the modo-mcp README; keep the file with its token out
of the repo). The save tool is allowed only in the turn that confirms, so the
recording itself proves no earlier turn could send anything:

    python3 scripts/record_ai_skills_eval_history.py --save /path/to/modo-mcp.json

It records: assessment, "Save this to my Modo passport." (the record shown),
then three branches from there: "Drop quote 4." (DROPPED_QUOTE in
check_eval_records.py), "Scores only, no quotes." and
"Yes, send it." (a real save to the local server). It refuses to write if a
turn does not look as expected (no record shown, wrong number of quotes, a
save before the confirmation turn).
"""

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_eval_records import (  # noqa: E402
    DROPPED_QUOTE, EXPECT_SAVE_QUOTES, SAVE_TOOL, without_quote)
from validate_assessment_record import last_json_block, validate  # noqa: E402

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


def resume(session: str, prompt: str, workdir: pathlib.Path,
           mcp: pathlib.Path | None = None, allow: str = "") -> None:
    cmd = ["claude", "-p", "--resume", session, "--plugin-dir", str(PLUGIN),
           "--allowedTools", "Read,Glob,Grep,Skill" + allow]
    if mcp:
        cmd += ["--mcp-config", str(mcp), "--strict-mcp-config"]
    subprocess.run(cmd, input=prompt, text=True, cwd=workdir, check=True, capture_output=True)


def fork(path: pathlib.Path) -> tuple[str, pathlib.Path]:
    """Copy a session file under a new session id, to branch from it."""
    session = str(uuid.uuid4())
    new = path.with_name(f"{session}.jsonl")
    rows = []
    for raw in path.read_text().splitlines():
        msg = json.loads(raw)
        if "sessionId" in msg:
            msg["sessionId"] = session
        rows.append(json.dumps(msg))
    new.write_text("\n".join(rows) + "\n")
    return session, new


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


SAVE_REQUEST = "Save this to my Modo passport."
SERVER_SAVE_TOOL = f"mcp__modo__{SAVE_TOOL}"  # the MCP config names the server "modo"


def tool_calls(history: str, name: str) -> int:
    n = 0
    for raw in history.splitlines():
        content = json.loads(raw)["message"].get("content")
        if isinstance(content, list):
            n += sum(1 for b in content if b.get("type") == "tool_use" and b.get("name") == name)
    return n


def shown(history: str, quotes: int, before: dict | None = None) -> dict:
    """The record the last reply showed; refuse if it is not a valid record with `quotes` quotes."""
    record = last_json_block(last_text(history))
    if record is None or validate(record) or len(record.get("evidence", [])) != quotes:
        sys.exit(f"recorded turn does not show a valid record with {quotes} quotes; not writing")
    if before is not None and {k: v for k, v in record.items() if k != "evidence"} != \
            {k: v for k, v in before.items() if k != "evidence"}:
        sys.exit("recorded turn changed more than the quotes; not writing")
    if tool_calls(history, SERVER_SAVE_TOOL):
        sys.exit("recorded history calls save_assessment before the confirmation turn; not writing")
    return record


def record_save(mcp: pathlib.Path) -> None:
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp).resolve()
        session, path = seed(workdir)
        paths = [path]
        try:
            resume(session, (SEED / "prompt.md").read_text(), workdir, mcp)
            if "Modo passport" not in last_text(clean(path, workdir)):
                sys.exit("recorded assessment does not offer saving to the Modo passport; not writing")
            resume(session, SAVE_REQUEST, workdir, mcp)
            out["shown"] = clean(path, workdir)
            first = shown(out["shown"], EXPECT_SAVE_QUOTES["save-confirmed"])
            for key, prompt, quotes in (
                    ("dropped", f"Drop quote {DROPPED_QUOTE}.", EXPECT_SAVE_QUOTES["save-quote-dropped"]),
                    ("scores", "Scores only, no quotes.", EXPECT_SAVE_QUOTES["save-scores-only"])):
                branch, bpath = fork(path)
                paths.append(bpath)
                resume(branch, prompt, workdir, mcp)
                out[key] = clean(bpath, workdir)
                record = shown(out[key], quotes, first)
                if key == "dropped" and record != without_quote(first, DROPPED_QUOTE):
                    sys.exit(f"recorded drop turn did not drop exactly quote {DROPPED_QUOTE}; not writing")
            branch, bpath = fork(path)
            paths.append(bpath)
            resume(branch, "Yes, send it.", workdir, mcp, allow="," + SERVER_SAVE_TOOL)
            out["saved"] = clean(bpath, workdir)
            if tool_calls(out["saved"], SERVER_SAVE_TOOL) != 1 or "passport" not in last_text(out["saved"]):
                sys.exit("recorded confirmation turn did not save once and offer the passport; not writing")
        finally:
            for p in paths:
                p.unlink(missing_ok=True)
            try:
                path.parent.rmdir()
            except OSError:
                pass
    targets = {"shown": ("save-confirmed", "save-declined", "save-edit-reshows", "save-rejected"),
               "dropped": ("save-quote-dropped",), "scores": ("save-scores-only",),
               "saved": ("passport-shown",)}
    for key, cases in targets.items():
        for case in cases:
            (EVALS / case / "history.jsonl").write_text(out[key])
    print("wrote history.jsonl to", ", ".join(c for cs in targets.values() for c in cs))


def record_decline() -> None:
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


def main(argv: list) -> None:
    if argv[:1] == ["--save"] and len(argv) == 2:
        record_save(pathlib.Path(argv[1]).resolve())
    else:
        record_decline()


if __name__ == "__main__":
    main(sys.argv[1:])
