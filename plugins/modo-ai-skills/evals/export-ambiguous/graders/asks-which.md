---
type: llm
weight: 3
---

The export contains two chats both called "Budget review": one dated 20 August 2026 and one dated 18 September 2026 (it also holds an unrelated "Lease question" chat). The user did not say which.

PASS if the response asks the user which one they mean, in a short question that tells the two apart (by date, or by date and first message), gives no capability scores or levels, and does not state or imply that it picked one.
FAIL if it assesses either chat, guesses which one is meant, gives any level or score, or fails to ask.
