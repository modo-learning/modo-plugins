---
type: llm
weight: 3
---

The user confirmed four chats: "CSV merge drops rows", "Pro plan price rise", "Team offsite agenda"
and "Cover letter". The cover letter chat has 3 typed user messages. The pricing chat shows strong
verification (the user recomputes figures and has them fixed). In the offsite chat the user accepts
every answer unchecked and hands over whole jobs ("whatever you think is best").

PASS if the response has a per-chat table with one row for each of the four chats, where
(1) the Cover letter row says too short and has no levels;
(2) the Pro plan price rise row gives Verification (V) a level of 4 or 5;
(3) every level shown in the Team offsite agenda row is 1 or 2;
(4) no row gives any capability a level for a chat it marks as too short.
FAIL if a row is missing, a chat other than these four appears, or any of (1) to (4) does not hold.
