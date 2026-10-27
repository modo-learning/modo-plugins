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
    # Strong verification, weak delegation (7 user messages).
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
        ("Those assumptions aren't in my data. Rerun it three ways: no change in churn, 5% extra churn, 10% extra churn. I'll check the three results against my own spreadsheet before they go in the deck.",
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
