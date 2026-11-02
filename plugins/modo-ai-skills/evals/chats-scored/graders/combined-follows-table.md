---
type: llm
weight: 2
---

Combined levels must follow fixed arithmetic over the per-chat table: for each capability, the
level is the median of the levels of the scored chats where it was shown, and with an even number
of such chats the lower of the two middle ones. A capability shown in no scored chat is "Not shown
in these chats" with no level.

PASS if every combined capability level in the response equals that median of the levels in its own
per-chat table (check each capability).
FAIL if any combined level differs from that median, or the response has no per-chat table.
