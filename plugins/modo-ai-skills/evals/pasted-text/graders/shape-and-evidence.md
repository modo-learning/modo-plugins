---
type: llm
weight: 2
---

The response should assess five capabilities: Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking.

PASS if ALL of these hold:
(1) All five capabilities appear, each with a level 1-5 or an explicit "not shown" marker, and each level has a confidence label (low, medium or high).
(2) Every quote on an "Evidence:" line is a word-for-word excerpt of one of the user's messages listed below. None comes from the assistant, from tool output or from another chat.
(3) Each capability has a line about what the next level would look like.
Only the quotes on "Evidence:" lines are graded for (2). Text in quotation marks inside a "Next level" line is suggested wording or commentary, not evidence, and is not checked.
FAIL if any of these does not hold.

The judge cannot see the chat, so here are all of the user's messages in it, verbatim. A quote is real if it is a word-for-word excerpt of one of these (any assistant text, tool output or header line is not a user message):

1. Write the launch email for our new invoice reminders feature. Audience: existing customers on the Team plan, who pay by card. Tone: plain and friendly, under 120 words, one call to action.
2. The call to action should link to the settings page, not the homepage. Also you said 'we'll nudge late payers for you' but reminders only go out to customers who have an email on file. Say that.
3. Good. I need the same email for the Starter plan, but they pay by bank transfer, so drop the card line and keep everything else identical.
4. Before I send it, list every claim in the email that I should confirm with the product team.
5. Confirmed 1 and 2 with product, 3 is wrong, Starter doesn't get it until November. Remove that and give me a one-line subject for each plan.
