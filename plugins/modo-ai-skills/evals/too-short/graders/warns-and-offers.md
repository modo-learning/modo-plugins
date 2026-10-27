---
type: llm
weight: 3
---

The chat has only two messages from the user.

PASS if the response says the chat is too short to judge (it states a minimum, which is 4 messages from the user), gives no capability scores or levels at all, and offers to assess a longer chat.
FAIL if it scores or rates any capability, guesses a level, or gives a verdict on how good the user is, or never says the chat is too short.
