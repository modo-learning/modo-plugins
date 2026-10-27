---
type: llm
weight: 3
---

The user's chat shows them recomputing the assistant's numbers, catching an error, demanding sources, asking for the arithmetic and assumptions, and checking results against their own spreadsheet (strong verification). It also shows them handing over the recommendations and then the whole deck with no brief ("whatever you think are best", "finish the rest of the deck, all the slides") (weak delegation).

PASS if the response gives Verification a level of 4 or 5 AND gives Delegation a level of 1 or 2 (shown as "Level N of 5" or equivalent), and Verification is rated higher than Delegation.
FAIL if Verification is below 4, or Delegation is above 2, or either is "not shown", or the levels are missing.
