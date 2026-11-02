---
type: llm
weight: 3
---

The export holds two chats. The one the user named, "Cover letter draft" (2026-10-15), has only two messages from the user (asking for a cover letter for a marketing coordinator role at a small bakery chain, then "Make it shorter and more confident.").

PASS if the response names the chat "Cover letter draft", says it is too short to judge, states the minimum of 4 messages from the user, gives no capability scores or levels, and offers to assess a longer chat.
FAIL if it scores, rates or hints at a level for any capability, assesses a different chat, or never says the chat is too short.
