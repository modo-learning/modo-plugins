"""Write the stability eval cases (ticket 33) from the golden chats.

Golden chats: scripts/fixtures/stability/<id>/chat.json (turns, planted
behaviours, expected bands; see the README there). Cases go to
plugins/modo-ai-skills/evals-stability/, a separate eval dir, so the normal
`claude plugin eval` run never starts them (they are many paid runs). The
folder is git-ignored and written before each run: committed, it would ship
with a marketplace install and push the plugin over the 512-file store limit.

- stab-<id>: the chat as the current chat's history, then "How good am I at
  using AI? Judge this chat." (as strong-verify-weak-delegate).
  Johnny's examples show only the user's messages, so Claude's turns there are
  a placeholder.
- stab-multi-set: assess-my-chats over the multi-chat set, with the two
  past-chat tools mocked as in the chats-* cases (gen_multi_chat_evals.py):
  the history holds the list already shown, and the user says yes.

The graders only check the answer's shape; the stability numbers come from
scripts/stability_report.py, which reads every run's final message (carried
in the LLM grader's evidence, see check_eval_records.final_text).

Run before a stability run (from any folder):

    python3 -I scripts/gen_stability_evals.py

Last 30 days: the multi-chat list shows chats dated 2026-10-22 to 2026-10-30.
From 2026-11-21 on, the skill's 30-day default no longer holds them all;
the history's list is already shown and confirmed, so the case still runs,
but move the dates forward if a run starts listing chats again.
"""

import json
import pathlib
import shutil
import sys
import uuid

SCRIPTS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import gen_multi_chat_evals as gm  # noqa: E402
from gen_ai_skills_eval_history import row  # noqa: E402
from stability_report import MULTI_SET, MULTI_SET_CHATS, golden_chats  # noqa: E402

OUT = SCRIPTS.parent / "plugins" / "modo-ai-skills" / "evals-stability"
ASK_SINGLE = "How good am I at using AI? Judge this chat."
RUNS = 5

SHAPE_SINGLE = gm.g_llm("""
PASS if the response is an assessment that gives all five capabilities (Problem Solving, Verification,
Workflow Design, Delegation, Strategic Thinking), each as "Level N of 5" or "Not shown in this chat", one
line starting "This chat:" with a title or "No title yet", and one line with the task type, agent session and
reused saved work.
FAIL otherwise. This grader only checks the shape; the levels are compared across runs elsewhere.
""")
SHAPE_MULTI = gm.g_llm("""
PASS if the response is an assessment across several chats that gives all five capabilities, each as
"Level N of 5" or "Not shown in these chats", one line with the title ("Your title:") or "N of 10 chats to
your title", one line with the task range and reused saved work, and a per-chat table with columns Title, P, V,
W, D and S.
FAIL otherwise. This grader only checks the shape; the levels are compared across runs elsewhere.
""")


def case_yaml(name, description, history, max_turns, timeout, allowed):
    lines = ['schema_version: "1.1"', f"name: {name}", f"description: {json.dumps(description)}",
             'plugins: ["../.."]', f"runs: {RUNS}"]
    lines += ["context:", "  history_file: history.jsonl"] if history else []
    lines += ["execution:", f"  max_turns: {max_turns}", f"  timeout_seconds: {timeout}",
              f"  allowed_tools: [{', '.join(allowed)}]"]
    return "\n".join(lines) + "\n"


def single_history(chat):
    session = str(uuid.uuid5(uuid.NAMESPACE_URL, "stab-" + chat["id"]))
    rows, parent, n = [], None, 0
    for t in chat["turns"]:
        for role, text in (("user", t["user"]), ("assistant", t["assistant"])):
            n += 1
            r = row(role, text, parent, n, session)
            rows.append(r)
            parent = r["uuid"]
    return rows


def single_case(chat):
    name = "stab-" + chat["id"]
    return name, {
        "case.yaml": case_yaml(name, f"Stability (ticket 33): {chat['title']} as the current chat; "
                                     "levels are compared across runs by stability_report.py.",
                               True, 15, 900, ["Read", "Glob", "Grep", "Skill"]),
        "prompt.md": ASK_SINGLE + "\n",
        "graders/shape.md": SHAPE_SINGLE,
        "graders/label.md": gm.LABEL_LAST,
        "graders/skill-fired.md": gm.g_tool("Skill", r'"skill"\s*:\s*"(?:[\w-]+:)?assess-my-ai-work"'),
        "history.jsonl": "".join(json.dumps(r) + "\n" for r in single_history(chat)),
    }


def chat_id(chat):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "stability-" + chat["id"]))[:8] + "-" + chat["id"]


def multi_case(chats):
    chats = sorted(chats, key=lambda c: c["updated_at"], reverse=True)
    listing = {"chats": [{"chat_id": chat_id(c), "title": c["title"], "updated_at": c["updated_at"]} for c in chats]}
    reply = "\n".join(
        ["Here are your chats from the last 30 days, up to 15 chats, newest first. Nothing has been read yet.", ""]
        + [f"{n}. {c['title']} ({c['updated_at'][:10]})" for n, c in enumerate(chats, 1)]
        + ["", "The current chat is left out.",
           "Chats with fewer than 4 typed user messages are listed but will come back as too short to score.",
           "Untick chats by number, change the date range or the number of chats (up to 25), or say yes to start."])
    session = str(uuid.uuid5(uuid.NAMESPACE_URL, "stab-" + MULTI_SET))
    rows, parent = [], None
    for n, (role, content) in enumerate([
            ("user", gm.ASK),
            ("assistant", [{"type": "tool_use", "id": "toolu_list_1", "name": gm.LIST, "input": {"n": 20}}]),
            ("user", [{"type": "tool_result", "tool_use_id": "toolu_list_1", "content": json.dumps(listing)}]),
            ("assistant", [{"type": "text", "text": reply}])], 1):
        r = {"parentUuid": parent, "isSidechain": False, "type": role, "message": {"role": role, "content": content},
             "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{session}-{n}")),
             "timestamp": f"2026-11-03T09:{n:02d}:00.000Z", "cwd": "/workspace", "sessionId": session}
        rows.append(r)
        parent = r["uuid"]
    name = "stab-" + MULTI_SET
    m = f"mocks/{gm.SERVER}"
    files = {
        "case.yaml": case_yaml(name, "Stability (ticket 33): assess-my-chats over the 6-chat multi-chat set; "
                                     "combined levels are compared across runs by stability_report.py.",
                               True, 40, 2400, ["Read", "Glob", "Grep", "Skill", "Agent"]),
        "prompt.md": "Yes, go ahead with all of them.\n",
        "graders/shape.md": SHAPE_MULTI,
        "graders/label.md": gm.LABEL_LAST,
        "graders/skill-fired.md": gm.SKILL_FIRED,
        "history.jsonl": "".join(json.dumps(r) + "\n" for r in rows),
        f"{m}/{gm.LIST_TOOL}.md": json.dumps(listing, indent=1) + "\n",
        f"{m}/{gm.READ_TOOL}.md": gm.READ_BODY,
        f"{m}/_tools.json": json.dumps(gm.TOOLS, indent=1) + "\n",
    }
    for c in chats:
        turns = [{"role": role, "text": t[role]} for t in c["turns"] for role in ("user", "assistant")]
        page = {"chat_id": chat_id(c), "title": c["title"], "updated_at": c["updated_at"], "turns": turns}
        files[f"{m}/fixtures/{chat_id(c)}.json"] = json.dumps(page, indent=1, ensure_ascii=False) + "\n"
    return name, files


def all_cases():
    chats = golden_chats()
    cases = dict(single_case(c) for c in chats.values())
    cases.update([multi_case([chats[k] for k in MULTI_SET_CHATS])])
    return cases


def write(out=OUT):
    for name, files in all_cases().items():
        if (out / name).exists():
            shutil.rmtree(out / name)
        for rel, text in files.items():
            path = out / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        print(out / name)


if __name__ == "__main__":
    write()
