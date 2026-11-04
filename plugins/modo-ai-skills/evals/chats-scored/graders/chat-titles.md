---
type: llm
weight: 2
---

The per-chat table must have a Title column. Each scored chat's title follows from that chat's own
five levels by this fixed rule: Orchestrator needs at least 3 capabilities at 4 or higher including
Delegation, and an agent session; Delegator needs at least 3 at 3 or higher including Delegation; Practitioner
needs at least 3 at 2 or higher; Explorer needs at least 3 shown; otherwise No title yet. Scores that reach
Orchestrator with no agent session give Delegator. None of these chats has an agent session, so no chat is
Orchestrator. A too-short chat has a dash, not a title.

PASS if the table has a Title column and every scored row's title is what the rule gives for that row's
own levels (check the arithmetic; a dash in a level column is not shown).
FAIL if the column is missing, a title does not follow from its row, any chat is Orchestrator, or Multiplier
appears as a title.
