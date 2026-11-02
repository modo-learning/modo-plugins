---
type: llm
weight: 2
---

The chat list had 9 chats: 6 titled chats from the last 30 days, one chat with no title,
one chat flagged by the safety classifier (no title, content redacted) and one chat from September.

PASS if the response (1) shows the 6 titled chats as a numbered list with their dates, (2) says that
2 chats were skipped and why (no title; flagged by the safety classifier), (3) says that short chats
are listed but will come back as too short, and (4) asks the user to confirm, untick chats or change
the range before anything is read.
FAIL if it reads, scores or describes the content of any chat, lists the untitled or flagged chat,
does not count the skipped chats, or starts work without asking.
