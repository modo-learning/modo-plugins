"""Writes the hand-written "current chat" transcripts the eval cases resume.

Each case's history.jsonl is a minimal Claude Code session file (user and
assistant turns only). The case prompt becomes the next user turn, so the chat
under assessment is exactly the turns written here. Re-run after editing:

    python3 -I plugins/modo-ai-skills/evals/build_histories.py
"""

import json
import pathlib
import uuid

HERE = pathlib.Path(__file__).parent

CHATS = {
    # Strong verification, weak delegation, ad hoc workflow (7 user messages).
    # Steps are taken one at a time with the setup repeated (message 6), no plan
    # or reusable process. Used by the assess case and the improvement cases.
    "strong-verify-weak-delegate": [
        ("Write up my Q3 pricing analysis for the board. Revenue by tier. Q3: Starter $120k, Team $310k, Enterprise $570k. Q2: Starter $110k, Team $280k, Enterprise $450k.",
         "Q3 revenue was $1,000k against $840k in Q2, up 19.0%.\n\n| Tier | Q2 | Q3 | Growth |\n|---|---|---|---|\n| Starter | $110k | $120k | 9.1% |\n| Team | $280k | $310k | 14.3% |\n| Enterprise | $450k | $570k | 26.7% |\n\nEnterprise tiers typically grow 20-25% quarter on quarter in SaaS, so 26.7% is ahead of the norm."),
        ("Before I use any of this I recomputed the tier growth myself. Team is 310 against 280, which is 10.7%, not 14.3%. Show your calculation for every percentage and fix the table.",
         "You're right, I made an error. Starter: 120/110 - 1 = 9.1%. Team: 310/280 - 1 = 10.7%. Enterprise: 570/450 - 1 = 26.7%. Total: 1000/840 - 1 = 19.0%. Corrected table: Starter 9.1%, Team 10.7%, Enterprise 26.7%."),
        ("You also said enterprise tiers typically grow 20-25% quarter on quarter. What is that based on? Give me a source I can open, or tell me it's a guess so I can cut it.",
         "I can't point to a specific source for that figure. It was a general impression, not something I can cite, so please cut it."),
        ("ok. Now just write the recommendations section, whatever pricing changes you think are best, I don't have time to think about it.",
         "Recommendations: (1) raise Starter by 10%, (2) offer an annual-billing discount on Team, (3) add a premium support add-on to Enterprise. Together these should add about $45k per quarter."),
        ("Where does the $45k come from? Walk me through the arithmetic with the numbers I gave you, and tell me which assumptions you made that I didn't give you.",
         "The $45k assumes Starter keeps 100% of its users after the increase (+$12k), 30% of Team customers take the annual discount at a 5% cost (-$4.6k) and a 15% attach rate for support add-ons on Enterprise (+$38k). The attach rate and the Team take-up are my assumptions, not from your data."),
        ("Those assumptions aren't in my data. Same board pricing analysis as before, Starter $120k, Team $310k, Enterprise $570k in Q3 and $110k, $280k, $450k in Q2. Rerun it three ways: no change in churn, 5% extra churn, 10% extra churn. I'll check the three results against my own spreadsheet before they go in the deck.",
         "No extra churn: +$45.4k per quarter. 5% extra churn: +$24.9k. 10% extra churn: +$4.4k."),
        ("The first two match my spreadsheet within rounding, the third is off by $2k, so fix that one. Then finish the rest of the deck, all the slides.",
         "Corrected the 10% churn case to +$2.4k. Here is a full ten-slide deck outline with speaker notes for each slide."),
    ],
    # Tactical chat: nothing bears on strategic thinking (7 user messages).
    "no-strategy": [
        ("Convert these dates to YYYY-MM-DD: 3/4/2026, 12/11/2025, 1/9/2026",
         "2026-03-04, 2025-12-11, 2026-01-09 (read as month/day/year)."),
        ("They're UK format, day first. Redo.",
         "2026-04-03, 2025-11-12, 2026-09-01."),
        ("Now give me a pandas one-liner that does that for a column called order_date.",
         "df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True).dt.strftime('%Y-%m-%d')"),
        ("It throws a ValueError on a blank cell. Fix it.",
         "Add errors='coerce': pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d'). Blank cells become NaN."),
        ("Rename these columns to snake_case: Order ID, Customer Name, Ship Date, Total (USD)",
         "order_id, customer_name, ship_date, total_usd"),
        ("Write a regex that matches UK postcodes.",
         "^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$"),
        ("That matches 'SW1A 1AA' but not 'sw1a1aa'. Make it case-insensitive and allow no space.",
         "^[A-Za-z]{1,2}[0-9][A-Za-z0-9]? ?[0-9][A-Za-z]{2}$"),
    ],
    # Too short: two user messages.
    "too-short": [
        ("Help me write a cover letter for a marketing coordinator role at a small bakery chain.",
         "Dear Hiring Manager, I am excited to apply for the Marketing Coordinator role. I have two years of social media experience and a passion for food brands..."),
        ("Make it shorter and more confident.",
         "Dear Hiring Manager, I bring two years of social media results and a clear plan for growing your chain's local following. I would welcome the chance to talk."),
    ],
}


# ---- Extra sources (ticket 02): files and text that the cases point at -----

# A normal chat with 5 user messages, used pasted, inside an export and as the
# current chat of the no-browse case.
LAUNCH_CHAT = [
    ("Write the launch email for our new invoice reminders feature. Audience: existing customers on the Team plan, who pay by card. Tone: plain and friendly, under 120 words, one call to action.",
     "Subject: Invoice reminders are here. Hi there, you can now send automatic reminders for unpaid invoices. Turn them on in Settings > Billing and we'll nudge late payers for you. Try it today."),
    ("The call to action should link to the settings page, not the homepage. Also you said 'we'll nudge late payers for you' but reminders only go out to customers who have an email on file. Say that.",
     "Subject: Invoice reminders are here. You can now send automatic reminders for unpaid invoices to customers who have an email on file. Turn them on at the link to your billing settings."),
    ("Good. I need the same email for the Starter plan, but they pay by bank transfer, so drop the card line and keep everything else identical.",
     "Here is the Starter version: same copy, with the card line removed."),
    ("Before I send it, list every claim in the email that I should confirm with the product team.",
     "Claims to confirm: (1) reminders go only to customers with an email on file; (2) the setting lives under Settings > Billing; (3) it is available on Starter and Team."),
    ("Confirmed 1 and 2 with product, 3 is wrong, Starter doesn't get it until November. Remove that and give me a one-line subject for each plan.",
     "Team: Invoice reminders are here. Starter: coming in November."),
]

# Ticket 03: the improvement cases assess the same planted chats as above.
CHATS["improve-weak-capabilities"] = CHATS["strong-verify-weak-delegate"]
CHATS["improve-not-shown"] = CHATS["no-strategy"]

# Current chat for the no-browse case (5 user messages).
CHATS["current-chat-only"] = LAUNCH_CHAT

# Distractors for the export file. Distinctive phrases let regex graders prove
# that only the chosen chat was read.
LEASE_CHAT = [
    "Can you explain the zebra-lease-clause in my flat contract?",
    "What does 'quiet enjoyment' mean there?",
    "Summarise my notice period obligations.",
    "Draft a polite email asking the landlord to fix the boiler.",
]
BUDGET_AUG = [
    "Build a budget template for the design team for August.",
    "Add a row for contractors.",
    "Totals are wrong, the sum of column C should be 41,200.",
    "Fine, export it as CSV.",
]
BUDGET_SEP = [
    "Build a budget template for the design team for September.",
    "Add a travel row.",
    "Rename the sheet to sep-budget-final.",
    "Fine, export it as CSV.",
]


def _export_chat(uuid_, name, day, users, assistants=None):
    msgs = []
    for i, u in enumerate(users):
        t = f"2026-{day}T10:{i * 2:02d}:00Z"
        msgs.append({"sender": "human", "text": u, "created_at": t})
        a = assistants[i] if assistants else "Done."
        msgs.append({"sender": "assistant", "text": a, "created_at": t})
    return {"uuid": uuid_, "name": name, "created_at": f"2026-{day}T10:00:00Z",
            "updated_at": f"2026-{day}T11:00:00Z", "chat_messages": msgs}


def export_json(include_launch=True):
    chats = []
    if include_launch:
        chats.append(_export_chat("c-launch", "Launch email copy", "10-14",
                                  [u for u, _ in LAUNCH_CHAT], [a for _, a in LAUNCH_CHAT]))
    chats.append(_export_chat("c-lease", "Lease question", "10-12", LEASE_CHAT))
    chats.append(_export_chat("c-bud-aug", "Budget review", "08-20", BUDGET_AUG))
    chats.append(_export_chat("c-bud-sep", "Budget review", "09-18", BUDGET_SEP))
    return json.dumps(chats, indent=1)


def session_rows():
    """A Claude Code style session: 5 typed user messages, plus user-role rows
    that only carry tool_result blocks (not written by the user)."""
    sid = str(uuid.uuid5(uuid.NAMESPACE_URL, "session-file"))
    rows, parent, n = [], None, 0

    def add(kind, content):
        nonlocal parent, n
        n += 1
        r = {
            "parentUuid": parent, "isSidechain": False, "type": kind,
            "message": {"role": kind, "content": content},
            "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{sid}-{n}")),
            "timestamp": f"2026-10-21T09:{n:02d}:00.000Z",
            "cwd": "/home/dev/shop", "sessionId": sid, "version": "2.0.0",
        }
        rows.append(r)
        parent = r["uuid"]

    def tool_use(i, name, inp, text=""):
        blocks = [{"type": "text", "text": text}] if text else []
        blocks.append({"type": "tool_use", "id": f"toolu_{i}", "name": name, "input": inp})
        add("assistant", blocks)

    def tool_result(i, out):
        add("user", [{"type": "tool_result", "tool_use_id": f"toolu_{i}", "content": out}])

    add("user", "The test tests/test_totals.py::test_discount_rounding fails in this repo. Find out why before changing anything, and show me the failing output first.")
    tool_use(1, "Bash", {"command": "pytest tests/test_totals.py::test_discount_rounding -x"}, "Running the failing test first.")
    tool_result(1, "FAILED tests/test_totals.py::test_discount_rounding - assert 10.01 == 10.0")
    tool_use(2, "Read", {"file_path": "/home/dev/shop/totals.py"})
    tool_result(2, "def discount(price, pct):\n    return round(price * pct / 100, 2)\n")
    add("assistant", [{"type": "text", "text": "The discount is rounded after multiplying, so 10.005 becomes 10.01. I suggest rounding half down."}])
    add("user", "Don't pick that yet. The spec in docs/pricing.md says half-up to the cent. Check what the spec actually says and quote the line before you change the code.")
    tool_use(3, "Read", {"file_path": "/home/dev/shop/docs/pricing.md"})
    tool_result(3, "Discounts are rounded half-up to the nearest cent, after summing line items.")
    add("assistant", [{"type": "text", "text": "The spec says: 'Discounts are rounded half-up to the nearest cent, after summing line items.' The bug is that rounding happens per line item."}])
    add("user", "Good. Fix it so rounding happens once, after summing. Add two edge-case tests first: a total of 10.005 and a total of 0.")
    tool_use(4, "Edit", {"file_path": "/home/dev/shop/tests/test_totals.py", "old_string": "# edge cases", "new_string": "def test_half_up():\n    assert total([10.005]) == 10.01\n\ndef test_zero():\n    assert total([]) == 0"})
    tool_result(4, "The file /home/dev/shop/tests/test_totals.py has been updated.")
    tool_use(5, "Bash", {"command": "pytest tests/test_totals.py"}, "Now the fix, then the run.")
    tool_result(5, "3 passed in 0.04s")
    add("assistant", [{"type": "text", "text": "Rounding now happens once after summing; all three tests pass."}])
    add("user", "Run the whole suite, not just that file. I want to see the summary line, and tell me if anything else changed behaviour.")
    tool_use(6, "Bash", {"command": "pytest"})
    tool_result(6, "42 passed, 1 skipped in 1.9s")
    add("assistant", [{"type": "text", "text": "42 passed, 1 skipped. The skipped test was already skipped before my change."}])
    add("user", "Show me that the skipped test was skipped before, with git stash and a run on the old code, I don't take it on trust.")
    tool_use(7, "Bash", {"command": "git stash && pytest -rs && git stash pop"})
    tool_result(7, "SKIPPED [1] tests/test_export.py:12: needs network\n42 passed, 1 skipped")
    add("assistant", [{"type": "text", "text": "Confirmed: the same test is skipped on the old code, for needing network."}])
    return rows


def write_extras():
    cases = HERE
    # pasted text has no file; its prompt is written by hand.
    def put(case, name, text):
        d = cases / case / "resources"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text)
        print(d / name)

    put("export-file", "conversations.json", export_json())
    put("export-ambiguous", "conversations.json", export_json(include_launch=False))
    put("session-file", "session.jsonl", "".join(json.dumps(r) + "\n" for r in session_rows()))


def row(role, text, parent, n, session):
    content = text if role == "user" else [{"type": "text", "text": text}]
    return {
        "parentUuid": parent,
        "isSidechain": False,
        "type": role,
        "message": {"role": role, "content": content},
        "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{session}-{n}")),
        "timestamp": f"2026-10-20T10:{n:02d}:00.000Z",
        "cwd": "/workspace",
        "sessionId": session,
    }


for case, turns in CHATS.items():
    session = str(uuid.uuid5(uuid.NAMESPACE_URL, case))
    rows, parent, n = [], None, 0
    for user, assistant in turns:
        for role, text in (("user", user), ("assistant", assistant)):
            n += 1
            r = row(role, text, parent, n, session)
            rows.append(r)
            parent = r["uuid"]
    out = HERE / case / "history.jsonl"
    out.parent.mkdir(exist_ok=True)
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(out, len(rows))


write_extras()
