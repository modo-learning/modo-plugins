---
type: llm
weight: 2
---

The response must give one title for this chat, worked out from the five capability levels it gives, by this fixed rule (Johnny's scoring rules v1). Give the highest title whose rule is met: Orchestrator, Level 4: at least 3 of the 5 capabilities at Level 4 or higher, including Delegation, and an agent session. Delegator, Level 3: at least 3 at Level 3 or higher, including Delegation. Practitioner, Level 2: at least 3 at Level 2 or higher. Explorer, Level 1: at least 3 shown, at any level. Otherwise "No title yet". "Not shown" reaches no level. This chat has no agent or tools. For example, levels 5, 4, 3, 2 and not shown give Practitioner, because Delegation is below 3.

PASS if ALL of these hold:
(1) There is exactly one line starting "This chat:", placed before the first capability block.
(2) Its title and level are what the rule gives for the five levels the response itself shows (check the arithmetic, including the Delegation condition).
(3) Near it, a line says "One chat is a thin sample: your title comes from 10 scored chats" and names /assess-my-chats.
(4) A line gives the task type (one of: Writing and editing, Research and summarizing, Data analysis, Coding, Planning and decisions, Brainstorming, Learning, Operations and admin), the agent session as no, and whether saved work was reused.
(5) It gives no Multiplier or Level 5 title.
FAIL if the title line is missing, its title or level does not follow the rule from the response's own levels, or any of (3) to (5) does not hold.
