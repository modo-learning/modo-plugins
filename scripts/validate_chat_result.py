"""Validate one ChatResult: what a per-chat agent returns in the multi-chat assessment (stdlib only).

In /assess-my-chats every chat is read and scored by its own agent, which
returns only this small JSON object; the full chat never reaches the main
conversation. The main conversation checks each result here before combining
them: the shape, the rubric's levels and behaviour ids, and that every quote is
a word-for-word excerpt of the user message it names.

Shape (design: Modo workspace doc docs/ai-skills/DESIGN-multi-chat-assessment.md (not in this repo)):

{
  "chat_id": "514e1c85-...",            the past-chat tool's id
  "title": "Q3 pricing analysis",       as the tool returned it ("" if none)
  "updated_at": "2026-10-30T12:01:00Z", as the tool returned it (yyyy-mm-dd... )
  "turns_total": 37,                    turns the tool returned
  "user_messages": 11,                  typed user messages (the rubric's count)
  "unreadable_turns": 5,                user-side turns with no text (tool results)
  "attachments_seen": true,             a message mentions a file the tool did not return
  "truncated_turns": [7],               turns the tool cut short
  "too_short": false,                   fewer than 4 user messages: nothing scored
  "runs": 3,                            0 when too short, else 3 or 5
  "run_kind": "subagents",              "subagents" | "one_response" | "none"
  "agent_session": {                    the user directed an agent or tools; most runs decide
    "value": true,
    "quote": null,                      {"message": n, "text": "exact words"}, or null
    "tools": ["Bash", "Edit"]           tool names; a yes has a quote or tool names, a no has neither
  },
  "task_type": "Coding",                one of the 8 in TASK_TYPES; null when too short
  "reuse": {                            saved work was used; most runs decide
    "value": false,
    "quote": null                       a yes has a quote, a no has none
  },
  "capabilities": {
    "verification": {
      "level": 3,                       1-5 or "not_shown"
      "confidence": "medium",           low | medium | high
      "agreement": "3 of 3 runs",       "k of n runs" or "runs disagreed"
      "behaviours": ["V3b"],            rubric v1.2 ids
      "quotes": [{"message": 4, "text": "exact words"}]
    },
    ... all five capabilities, in rubric order
  }
}

Usage:
    python3 -I scripts/validate_chat_result.py result.json
    python3 -I scripts/validate_chat_result.py result.json --messages user_messages.json
(--messages: a JSON list of the chat's user messages in order, to check quotes.)
"""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from derive_levels import BEHAVIOURS  # noqa: E402
from rubric_common import (CAPABILITIES, CONFIDENCE, LEVEL_NOT_SHOWN, MAX_QUOTE, TASK_TYPES, is_date,  # noqa: E402
                           is_int, is_level)

PREFIX = {"problem_solving": "P", "verification": "V", "workflow_design": "W",
          "delegation": "D", "strategic_thinking": "S"}
RUN_KINDS = ("subagents", "one_response", "none")
MIN_USER_MESSAGES = 4
TOP = {"chat_id", "title", "updated_at", "turns_total", "user_messages", "unreadable_turns",
       "attachments_seen", "truncated_turns", "too_short", "runs", "run_kind", "agent_session",
       "task_type", "reuse", "capabilities"}
CAP_FIELDS = {"level", "confidence", "agreement", "behaviours", "quotes"}
AGREEMENT = re.compile(r"^([1-5]) of ([35]) runs$|^runs disagreed$")
# The past-chat tools put this before typed user messages (verified 2026-11-01).
REMINDER = re.compile(r"^\s*<system-reminder>.*?</system-reminder>\s*", re.S)


def clean_user_message(text: str) -> str:
    """A user message as the user typed it: the leading system-reminder removed."""
    return REMINDER.sub("", text, count=1)


def validate(result, messages=None):
    """Return a list of error strings; empty means valid.

    messages: the chat's user messages in order (raw or cleaned); when given,
    every quote must be a word-for-word excerpt of the message it names."""
    if not isinstance(result, dict):
        return ["result: must be a JSON object"]
    errors = []
    extra, missing = sorted(set(result) - TOP), sorted(TOP - set(result))
    if extra:
        errors.append(f"result: unknown field(s) {extra}")
    if missing:
        errors.append(f"result: missing field(s) {missing}")

    if "chat_id" in result and not (isinstance(result["chat_id"], str) and result["chat_id"].strip()):
        errors.append("chat_id: must be a non-empty string")
    if "title" in result and not isinstance(result["title"], str):
        errors.append("title: must be a string")
    if "updated_at" in result and not (isinstance(result["updated_at"], str) and is_date(result["updated_at"][:10])):
        errors.append("updated_at: must start with a yyyy-mm-dd date")
    for key in ("turns_total", "user_messages", "unreadable_turns"):
        if key in result and not is_int(result[key], 0):
            errors.append(f"{key}: must be an integer of 0 or more")
    for key in ("attachments_seen", "too_short"):
        if key in result and not isinstance(result[key], bool):
            errors.append(f"{key}: must be true or false")
    turns = result.get("truncated_turns")
    if "truncated_turns" in result and not (isinstance(turns, list) and all(is_int(t, 0) for t in turns)):
        errors.append("truncated_turns: must be a list of turn numbers")
    if "run_kind" in result and result["run_kind"] not in RUN_KINDS:
        errors.append(f"run_kind: must be one of {list(RUN_KINDS)}")

    too_short = result.get("too_short")
    users = result.get("user_messages")
    if isinstance(too_short, bool) and is_int(users, 0):
        if too_short != (users < MIN_USER_MESSAGES):
            errors.append(f"too_short: must be true exactly when user_messages is under {MIN_USER_MESSAGES}")
    runs = result.get("runs")
    if "runs" in result:
        allowed = (0,) if too_short is True else (3, 5)
        if runs not in allowed or isinstance(runs, bool):
            errors.append(f"runs: must be {' or '.join(map(str, allowed))}")
    if too_short is True and result.get("run_kind") != "none":
        errors.append('run_kind: must be "none" for a chat that is too short')
    if too_short is False and result.get("run_kind") == "none":
        errors.append('run_kind: "none" only for a chat that is too short')

    cleaned = [clean_user_message(m) for m in messages] if messages is not None else None
    errors += _signals(result, too_short, users, cleaned)

    caps = result.get("capabilities")
    if "capabilities" in result:
        if not isinstance(caps, dict):
            errors.append("capabilities: must be an object")
        else:
            if list(caps) != list(CAPABILITIES):
                errors.append(f"capabilities: must have exactly {list(CAPABILITIES)} in that order")
            for cap in CAPABILITIES:
                if isinstance(caps.get(cap), dict):
                    errors += _capability(cap, caps[cap], too_short, runs, users, cleaned)
                elif cap in caps:
                    errors.append(f"capabilities.{cap}: must be an object")
    return errors


def _signals(result, too_short, users, messages):
    """Agent session, task type and reuse (the brief, "Per chat, from the runs")."""
    errors = []
    agent = result.get("agent_session")
    if "agent_session" in result:
        if not (isinstance(agent, dict) and set(agent) == {"value", "quote", "tools"}
                and isinstance(agent["value"], bool)):
            errors.append("agent_session: must be exactly {value, quote, tools}")
        else:
            tools, quote = agent["tools"], agent["quote"]
            if not (isinstance(tools, list) and all(isinstance(t, str) and t.strip() for t in tools)):
                errors.append("agent_session.tools: must be a list of tool names")
                tools = []
            if agent["value"] and not (quote or tools):
                errors.append("agent_session: yes needs one exact quote or the tool names")
            if not agent["value"] and (quote or tools):
                errors.append("agent_session: no carries no quote or tools")
            if agent["value"] and too_short is True:
                errors.append("agent_session: must be no for a chat that is too short")
            if quote is not None:
                errors += _quote("agent_session.quote", quote, users, messages)
    if "task_type" in result:
        if too_short is True:
            if result["task_type"] is not None:
                errors.append("task_type: must be null for a chat that is too short")
        elif result["task_type"] not in TASK_TYPES:
            errors.append(f"task_type: must be one of {list(TASK_TYPES)}")
    reuse = result.get("reuse")
    if "reuse" in result:
        if not (isinstance(reuse, dict) and set(reuse) == {"value", "quote"} and isinstance(reuse["value"], bool)):
            errors.append("reuse: must be an object, exactly {value, quote}")
        else:
            if reuse["value"] and too_short is True:
                errors.append("reuse: must be no for a chat that is too short")
            if reuse["value"] and not reuse["quote"]:
                errors.append("reuse: yes needs a quote")
            if not reuse["value"] and reuse["quote"]:
                errors.append("reuse: no carries no quote")
            if reuse["quote"] is not None:
                errors += _quote("reuse.quote", reuse["quote"], users, messages)
    return errors


def _quote(where, q, users, messages):
    """Errors for one {message, text} quote; messages, when given, are the cleaned user messages."""
    if not (isinstance(q, dict) and set(q) == {"message", "text"}):
        return [f"{where}: must be exactly {{message, text}}"]
    text, n = q["text"], q["message"]
    if not (isinstance(text, str) and text.strip() and len(text) <= MAX_QUOTE):
        return [f"{where}.text: must be 1 to {MAX_QUOTE} characters and not blank"]
    if not (is_int(n, 1) and (not is_int(users, 0) or n <= users)):
        return [f"{where}.message: must be a user message number from 1 to user_messages"]
    if messages is not None:
        if n > len(messages):
            return [f"{where}.message: the chat has only {len(messages)} user messages"]
        if text not in messages[n - 1]:
            return [f"{where}.text: not a word-for-word excerpt of user message {n}"]
    return []


def _capability(cap, c, too_short, runs, users, messages):
    where = f"capabilities.{cap}"
    errors = []
    extra, missing = sorted(set(c) - CAP_FIELDS), sorted(CAP_FIELDS - set(c))
    if extra:
        errors.append(f"{where}: unknown field(s) {extra}")
    if missing:
        errors.append(f"{where}: missing field(s) {missing}")
    level = c.get("level")
    shown = level != LEVEL_NOT_SHOWN
    if not is_level(level):
        errors.append(f'{where}.level: must be an integer from 1 to 5 or "not_shown"')
    if c.get("confidence") not in CONFIDENCE:
        errors.append(f"{where}.confidence: must be one of {list(CONFIDENCE)}")
    agreement = c.get("agreement")
    m = AGREEMENT.match(agreement) if isinstance(agreement, str) else None
    if too_short is True:
        if level != LEVEL_NOT_SHOWN:
            errors.append(f'{where}.level: must be "not_shown" for a chat that is too short')
        if agreement != "":
            errors.append(f'{where}.agreement: must be "" for a chat that is too short')
    elif not m:
        errors.append(f'{where}.agreement: must be "k of n runs" (n = 3 or 5) or "runs disagreed"')
    elif m.group(2) and is_int(runs, 0) and int(m.group(2)) != runs:
        errors.append(f"{where}.agreement: says {m.group(2)} runs but runs is {runs}")
    elif m.group(1) and int(m.group(1)) > int(m.group(2)):
        errors.append(f"{where}.agreement: k is more than n")
    if agreement == "runs disagreed" and shown:
        errors.append(f'{where}.level: must be "not_shown" when the runs disagreed')

    behaviours = c.get("behaviours")
    if not isinstance(behaviours, list):
        errors.append(f"{where}.behaviours: must be a list")
        behaviours = []
    if len(behaviours) > 3:
        errors.append(f"{where}.behaviours: at most 3")
    for b in behaviours:
        if b not in BEHAVIOURS or not str(b).startswith(PREFIX[cap]):
            errors.append(f"{where}.behaviours: {b!r} is not a rubric v1.2 {cap} behaviour id")
    quotes = c.get("quotes")
    if not isinstance(quotes, list):
        errors.append(f"{where}.quotes: must be a list")
        quotes = []
    if not shown and (behaviours or quotes):
        errors.append(f"{where}: a not_shown capability has no behaviours or quotes")
    if shown and not quotes:
        errors.append(f"{where}.quotes: a capability with a level needs at least one quote")
    if len(quotes) > 3:
        errors.append(f"{where}.quotes: at most 3")
    for i, q in enumerate(quotes):
        errors += _quote(f"{where}.quotes.{i}", q, users, messages)
    return errors


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    msgs = None
    if "--messages" in args:
        i = args.index("--messages")
        msgs = json.loads(pathlib.Path(args[i + 1]).read_text())
        del args[i:i + 2]
    problems = validate(json.loads(pathlib.Path(args[0]).read_text()), msgs)
    for p in problems:
        print(p)
    sys.exit(1 if problems else 0)
