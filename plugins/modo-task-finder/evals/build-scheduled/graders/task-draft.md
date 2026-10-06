---
type: llm
weight: 2
---

The user asked to set up the Acme weekly status report as a scheduled task every Friday afternoon.

PASS if the response proposes a scheduled task with a name, the full prompt the task would run (covering the three sections done / in progress / risks, one page max, no internal ticket numbers, next week's milestones, for Dana at Acme), and a weekly Friday schedule (any afternoon time such as 2 pm or 3 pm counts), AND asks the user to confirm it or tells them how to create it, without claiming it has already been scheduled.
Offering to create it with a tool after the user confirms is fine.
FAIL if any of name, prompt or schedule is missing, or the response claims the task is already created or running.
