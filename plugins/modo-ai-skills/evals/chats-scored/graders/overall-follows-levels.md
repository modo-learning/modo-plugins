---
type: llm
weight: 2
---

The response must give one overall level on Modo's AI fluency ladder, worked out from the five
combined capability levels it gives, by this fixed rule: the overall level is the highest L from 1 to 4
such that at least 3 of the 5 capabilities have a combined level of L or higher ("not shown" reaches no
level). Titles: Level 1 Explorer, Level 2 Practitioner, Level 3 Delegator, Level 4 Orchestrator. Fewer
than 3 capabilities with a level gives "not enough shown". Level 5 (Multiplier) is never given. For
example, combined levels 4, 3, 3, 2 and not shown give Delegator (Level 3); 3, 2, 2, 2, 1 give
Practitioner (Level 2).

PASS if there is exactly one line starting "Overall:", placed before the first capability block, and
its title and level are what the rule gives for the combined levels the response itself shows (check
the arithmetic, using the combined levels, not the per-chat table).
FAIL if the overall line is missing or placed after the capability blocks, its title or level does
not follow the rule, or it gives Multiplier or Level 5 overall.
