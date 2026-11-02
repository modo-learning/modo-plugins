---
type: llm
weight: 3
---

The chat under assessment (the judge cannot see it) is seven small mechanical tasks (convert dates, a pandas one-liner, rename columns, a regex). Nothing in it bears on Strategic Thinking.

PASS if the response marks Strategic Thinking as "not shown" AND gives it no improvement (no technique and no "try this next time" prompt for it, and it is not one of the improved capabilities), AND the improvements section covers at most two capabilities, each of which the response itself scored with a level 1-5.
FAIL if Strategic Thinking, or any capability the response marked "not shown", gets an improvement, or more than two capabilities get one.
