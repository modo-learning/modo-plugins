---
type: llm
weight: 1
---

In the chats read, some user turns came back empty (answers picked in a question widget), one
Claude turn was cut ("[Output abbreviated due to length limit]") and one chat mentions an attached file
the tool cannot return.

PASS if the response mentions at least one of these gaps (unreadable or empty turns, a cut turn,
an attachment that could not be read), and never states or guesses what an empty turn said.
FAIL if it mentions none of them, or describes the content of an empty turn.
