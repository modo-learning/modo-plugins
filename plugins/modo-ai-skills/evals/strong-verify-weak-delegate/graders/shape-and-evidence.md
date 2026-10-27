---
type: llm
weight: 2
---

The response should assess the chat on exactly five capabilities: Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking.

PASS if ALL of these hold:
(1) All five capabilities appear, each with a level 1-5 or an explicit "not shown" marker.
(2) Each capability has a confidence label of low, medium or high.
(3) Each capability that has a level has one or two short quotes that really appear in the user's own messages in the chat (for example "Team is 310 against 280" or "finish the rest of the deck"). Quotes must be from the user, not the assistant, and not invented.
(4) Each capability has a line about what the next level up would look like.
FAIL if any capability is missing, any level lacks a confidence label, any quote is invented or taken from the assistant's turns, or the next-level lines are missing.
