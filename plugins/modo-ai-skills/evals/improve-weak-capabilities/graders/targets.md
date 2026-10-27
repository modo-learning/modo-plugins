---
type: llm
weight: 3
---

The chat the assessment covers (the judge cannot see it): the user asks for a Q3 pricing analysis for the board with revenue per tier, recomputes the percentages themselves and catches a wrong figure, demands a source for an unsupported industry statistic, asks for the arithmetic and assumptions behind a $45k estimate, and checks three reruns against their own spreadsheet (strong Verification). They hand over the recommendations with "whatever pricing changes you think are best, I don't have time to think about it" and the whole deck with "finish the rest of the deck, all the slides" and no brief (weak Delegation). They take the steps one at a time and re-paste the same Q3 and Q2 numbers in message 6 (weak, ad hoc Workflow Design).

Rubric ground truth for the step up. Delegation: level 1 hands over a whole job vaguely with no scope, role or output and does not look at it; level 2 hands over a whole task with a minimal brief, no review point and no decision kept; level 3 gives a clear task with scope and output format and keeps some decisions ("give me three options, I'll choose"); level 4 splits work on purpose, gives a role, inputs, constraints and what done looks like, and sets a review step before Claude carries on. Workflow Design: level 1 treats each request as stand-alone and re-explains context; level 2 moves through steps ad hoc with no plan stated and repeats setup; level 3 lays out steps in order and feeds earlier outputs into later steps; level 4 defines a repeatable process with a fixed format or rules, a template, stages with a check between them.

The response should contain assessment blocks for the five capabilities, followed by an improvements section for exactly two capabilities.

PASS if the improvements section (after the five blocks) covers exactly two capabilities, Verification is NOT one of them, and each of the two is one the response itself scored at the lowest levels among the capabilities it marked as shown (Delegation and Workflow Design are the planted weak ones; Strategic Thinking is an acceptable alternative only if the response scored it at the same level as, or lower than, one of them).
FAIL if Verification gets an improvement, if more than two capabilities get one, if a capability the response itself marked "not shown" gets one, or if there is no improvements section.
