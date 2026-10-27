---
type: llm
weight: 2
---

The response should assess five capabilities: Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking.

PASS if ALL of these hold:
(1) All five capabilities appear, each with a level 1-5 or an explicit "not shown" marker, and each level has a confidence label (low, medium or high).
(2) Every quote on an "Evidence:" line is a word-for-word excerpt of one of the user's messages listed below. None comes from the assistant, from tool output or from another chat.
(3) Each capability has a line about what the next level would look like.
(4) No quote is taken from a tool result or tool output (for example 'FAILED tests/', '42 passed', 'needs network'), and the response does not count tool results as messages from the user.
Only quotes on "Evidence:" lines are graded for the quote check. Text in quotation marks inside "Next level" lines or the Improvements section (techniques, "Try this next time" prompts) is suggested wording, not evidence, and is not checked.
FAIL if any of these does not hold.

The judge cannot see the chat, so here are all of the user's messages in it, verbatim. A quote is real if it is a word-for-word excerpt of one of these (any assistant text, tool output or header line is not a user message):

1. The test tests/test_totals.py::test_discount_rounding fails in this repo. Find out why before changing anything, and show me the failing output first.
2. Don't pick that yet. The spec in docs/pricing.md says half-up to the cent. Check what the spec actually says and quote the line before you change the code.
3. Good. Fix it so rounding happens once, after summing. Add two edge-case tests first: a total of 10.005 and a total of 0.
4. Run the whole suite, not just that file. I want to see the summary line, and tell me if anything else changed behaviour.
5. Show me that the skipped test was skipped before, with git stash and a run on the old code, I don't take it on trust.

An "Improvements" section after the five capability blocks (techniques, copy-ready prompts, a skill offer) is not one of the five blocks; ignore it for this check.
