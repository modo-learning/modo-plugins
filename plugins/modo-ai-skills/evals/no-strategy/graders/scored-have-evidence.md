---
type: llm
weight: 2
---

PASS if ALL of these hold:
(1) At least two of the other four capabilities (Problem Solving, Verification, Workflow Design, Delegation) are given a level 1-5, each with a confidence label (low, medium or high).
(2) Every capability that has a level has one or two short quotes that really appear in the user's own messages in this chat (for example "They're UK format, day first" or "It throws a ValueError on a blank cell"), not invented and not from the assistant.
(3) Every capability that has a level has a line about what the next level up would look like.
(4) No capability is rated Level 5 and none has high confidence on a chat this tactical.
FAIL otherwise.
