---
type: llm
weight: 3
---

Ground truth (the judge cannot see the chat). The assessment already given scored: Problem Solving level 3 medium; Verification level 3 low; Workflow Design not shown; Delegation level 3 low; Strategic Thinking not shown. The export plan proposed these four quotes:
1. Problem Solving: "It throws a ValueError on a blank cell. Fix it."
2. Verification: "That matches 'SW1A 1AA' but not 'sw1a1aa'. Make it case-insensitive and allow no space."
3. Delegation: "Now give me a pandas one-liner that does that for a column called order_date."
4. Problem Solving: "They're UK format, day first. Redo."
Title: Date and text cleanup tasks. Date: 2026-10-20. The user approved all four.

The record's capability keys are problem_solving, verification, workflow_design, delegation, strategic_thinking (mapping to Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking). Only the final fenced json block and the evidence list in the report are graded for quotes; table cells, headings and fixed explanatory text are not.

PASS if ALL hold:
(1) The final fenced json block is exactly one object with these top-level fields and no others: rubric_version "v1", capabilities (an object with exactly the five keys, each {level, confidence}, level an integer 1-5 or "not_shown", confidence "low", "medium" or "high"), evidence (a list of {capability, quote} items), session_title, session_date.
(2) problem_solving 3 medium, verification 3 low, workflow_design "not_shown" with confidence "low", delegation 3 low, strategic_thinking "not_shown" with confidence "low".
(3) evidence has exactly the four quotes above, word for word, tied to the capabilities named (problem_solving twice, verification, delegation), and no evidence item is tied to workflow_design or strategic_thinking.
(4) session_title is "Date and text cleanup tasks" and session_date "2026-10-20".
FAIL if any of these differ, a not-shown capability has a quote or a confidence other than low, or fields are extra or missing.
