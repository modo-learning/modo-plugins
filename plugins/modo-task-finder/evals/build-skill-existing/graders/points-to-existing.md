---
type: llm
weight: 2
---

The user asked for a skill for their candidate outreach messages. A shared skill called recruiting-messages, from the Northwind talent team, already writes first-touch LinkedIn messages to engineering candidates (under 90 words, salary band first, one profile detail). It does not cover the user's other rules: no buzzwords, and signing as Priya from Northwind.

PASS if the response names the existing recruiting-messages skill as already covering this job, does not present a new standalone outreach skill as the plan, and offers to use it as is or to tweak it for at least one of the missing rules (no buzzwords, or the Priya sign-off).
FAIL if the response drafts a complete new outreach skill without first pointing to recruiting-messages, ignores the existing skill, or claims a skill was installed or changed.
