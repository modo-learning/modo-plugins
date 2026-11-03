---
type: llm
weight: 2
---

The response must give one overall level on Modo's AI fluency ladder, worked out from the five capability levels it gives, by this fixed rule: the overall level is the highest L from 1 to 4 such that at least 3 of the 5 capabilities have a level of L or higher ("not shown" reaches no level). Titles: Level 1 Explorer, Level 2 Practitioner, Level 3 Delegator, Level 4 Orchestrator. Fewer than 3 capabilities with a level gives "not enough shown". Level 5 (Multiplier) is never given. For example, levels 5, 4, 3, 2 and not shown give Delegator (Level 3); levels 5, 3, 2, 2, 1 give Practitioner (Level 2).

PASS if ALL of these hold:
(1) There is exactly one line starting "Overall:", placed before the first capability block.
(2) Its title and level are what the rule gives for the five levels the response itself shows (check the arithmetic).
(3) Near it, a line says that one chat is a thin sample (or similar), mentions 30 days, and suggests /assess-my-chats.
(4) If the overall level is 4, a line says Level 5 (Multiplier) is not given from chats; if it is below 4, no Multiplier title is given to the user.
FAIL if the overall line is missing, its title or level does not follow the rule from the response's own levels, it gives Multiplier or Level 5 overall, or the thin-sample line is missing.
