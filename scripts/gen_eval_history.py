"""Generate the synthetic chat export used by modo-task-finder evals.

The export has planted patterns so evals can check what /my-tasks keeps and
drops. Every name, company and figure here is invented.

Planted, inside the window (2026-09-01 .. 2026-09-30):
  status-report   6 chats  weekly client status report, time-triggered   -> scheduled task
  outreach        5 chats  candidate outreach with the same rules        -> skill
  expenses        4 chats  expense reconciliation from Xero (not linked) -> needs a connector first
  investor        3 chats  monthly investor update (skill installed)     -> already covered
  newsletter      1 chat   team newsletter asked 4 times in one long chat -> kept (repeated requests)
  menu            2 chats  translating a cafe menu                       -> excluded (below 3)
  pricing         1 chat   long one-off pricing model build             -> excluded (one-off)
  misc            8 chats  unrelated one-offs                            -> excluded
Outside the window (August):
  talk-prep       4 chats  conference talk prep                          -> excluded (out of window)

Usage: python3 scripts/gen_eval_history.py > plugins/modo-task-finder/evals/planted-patterns/resources/conversations.json
"""

import json
import sys

def msg(sender, text, ts):
    return {"sender": sender, "text": text, "created_at": ts}

def chat(uid, name, day, turns, hour=10):
    ts = f"{day}T{hour:02d}:00:00Z"
    messages = []
    for i, (h, a) in enumerate(turns):
        t = f"{day}T{hour:02d}:{i*2:02d}:00Z"
        messages.append(msg("human", h, t))
        messages.append(msg("assistant", a, t))
    return {"uuid": uid, "name": name, "created_at": ts, "updated_at": ts,
            "chat_messages": messages}

chats = []

# status-report: every Friday-ish, same re-explanation each time
for i, day in enumerate(["2026-09-04", "2026-09-11", "2026-09-18",
                         "2026-09-25", "2026-09-29", "2026-09-30"]):
    chats.append(chat(f"sr-{i}", f"Acme weekly status report {day}", day, [
        ("Here are this week's Jira notes for the Acme project. Turn them into the "
         "weekly client status report. Same format as always: three sections "
         "(done, in progress, risks), max one page, no internal ticket numbers, "
         "and end with next week's milestones. It goes to Dana at Acme every Friday.",
         "Here is the Acme weekly status report in the usual three-section format..."),
        ("Shorten the risks part and make the tone less alarming.",
         "Updated the risks section..."),
    ], hour=16))

# outreach: same hiring rules re-explained
for i, day in enumerate(["2026-09-02", "2026-09-09", "2026-09-15",
                         "2026-09-22", "2026-09-28"]):
    chats.append(chat(f"or-{i}", f"Candidate outreach message {i+1}", day, [
        ("Write a LinkedIn outreach message to this backend engineer candidate. "
         "Rules: under 90 words, mention one specific thing from their profile, "
         "say the salary band up front (90-110k), no buzzwords, sign off as "
         "Priya from Northwind.",
         "Hi Sam, I saw your talk on Postgres partitioning..."),
    ]))

# expenses: Xero not connected, manual paste every time
for i, day in enumerate(["2026-09-05", "2026-09-12", "2026-09-19", "2026-09-26"]):
    chats.append(chat(f"ex-{i}", f"Reconcile team expenses week {i+1}", day, [
        ("I exported this week's card transactions from Xero again and pasted them "
         "below. Match them to the receipts list, flag anything without a receipt, "
         "and group by cost centre.",
         "Matched 41 of 44 transactions. Three have no receipt..."),
        ("Can you also total by cost centre?", "Totals by cost centre..."),
    ]))

# investor: monthly update, user has an investor-update skill installed
for i, day in enumerate(["2026-09-01", "2026-09-14", "2026-09-30"]):
    chats.append(chat(f"iv-{i}", f"Investor update draft {i+1}", day, [
        ("Use my investor-update skill to draft this month's investor update from "
         "these metrics. The team's edits came in late again so I need to redo "
         "the personalised versions.",
         "Drafted the update with the investor-update skill..."),
    ]))

# newsletter: one long-running chat the user keeps coming back to, 4 requests
news_msgs = []
for n, day in enumerate(["2026-09-07", "2026-09-14", "2026-09-21", "2026-09-28"]):
    t = f"{day}T09:00:00Z"
    news_msgs.append(msg("human",
        "Same as last week: turn these notes into the internal team newsletter. "
        "Friendly tone, max 250 words, sections Wins / Shout-outs / Coming up, "
        "and end with the office plant joke.", t))
    news_msgs.append(msg("assistant", f"Here's this week's newsletter ({day})...", t))
chats.append({"uuid": "nl-0", "name": "Team newsletter", "created_at": "2026-09-07T09:00:00Z",
              "updated_at": "2026-09-28T09:00:00Z", "chat_messages": news_msgs})

# menu: only two chats, must be excluded
for i, day in enumerate(["2026-09-08", "2026-09-23"]):
    chats.append(chat(f"mn-{i}", f"Translate cafe menu to Spanish {i+1}", day, [
        ("Translate this cafe menu into Spanish.", "Aquí está el menú..."),
    ]))

# pricing: one long one-off session, must be excluded
pricing_turns = [(f"Pricing model step {n}: adjust the tier assumptions and "
                  f"recompute margins for scenario {n}.",
                  f"Recomputed scenario {n}...") for n in range(1, 16)]
chats.append(chat("pr-0", "Build 2027 pricing model", "2026-09-17", pricing_turns))

# misc one-offs
misc = [
    ("2026-09-03", "Birthday gift ideas for my dad"),
    ("2026-09-06", "Fix Python KeyError in a script"),
    ("2026-09-10", "Visa requirements for Japan"),
    ("2026-09-13", "Summarise an article on remote work"),
    ("2026-09-16", "Weekend recipe with chickpeas"),
    ("2026-09-20", "Explain how index funds work"),
    ("2026-09-24", "Draft a toast for a wedding"),
    ("2026-09-27", "Compare two laptops"),
]
for i, (day, name) in enumerate(misc):
    chats.append(chat(f"mi-{i}", name, day, [(name + ", please.", "Sure...")]))

# talk-prep: repeated, but in August (outside the window)
for i, day in enumerate(["2026-08-05", "2026-08-12", "2026-08-19", "2026-08-26"]):
    chats.append(chat(f"tp-{i}", f"Conference talk prep {i+1}", day, [
        ("Help me rehearse my conference talk on data pipelines. Same structure: "
         "hook, three lessons, demo, Q&A prep.", "Let's go through the hook..."),
    ]))

chats.sort(key=lambda c: c["created_at"], reverse=True)
json.dump(chats, sys.stdout, indent=1, ensure_ascii=False)
sys.stdout.write("\n")
