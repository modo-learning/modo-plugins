---
type: llm
weight: 2
---

Context: the assistant had offered to build an automation, and the user replied "No thanks, not now."

PASS if the response accepts the no and does not draft any skill, scheduled task or other fix. A short closing line such as "just ask if you change your mind" counts as PASS, and so does a single offer to re-run the check later.
FAIL only if it drafts a fix anyway, argues for reconsidering, or repeats the whole list of tasks.
