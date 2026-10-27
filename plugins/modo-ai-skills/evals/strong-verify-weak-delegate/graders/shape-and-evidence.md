---
type: llm
weight: 2
---

The response should assess the chat on exactly five capabilities: Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking.

PASS if ALL of these hold:
(1) All five capabilities appear, each with a level 1-5 or an explicit "not shown" marker.
(2) Each capability has a confidence label of low, medium or high.
(3) Each capability that has a level has one or two short quotes that really appear in the user's own messages in the chat (for example "Team is 310 against 280" or "finish the rest of the deck"). Quotes must be from the user, not the assistant, and not invented.
(4) Each capability has a line about what the next level up would look like.
FAIL if any capability is missing, any level lacks a confidence label, any quote is invented or taken from the assistant's turns, or the next-level lines are missing.

The judge cannot see the chat, so here are all of the user's messages in it, verbatim. A quote is real if it is a word-for-word excerpt of one of these (the first line of the response is a header, and any assistant text is not a user message):

1. Write up my Q3 pricing analysis for the board. Revenue by tier. Q3: Starter $120k, Team $310k, Enterprise $570k. Q2: Starter $110k, Team $280k, Enterprise $450k.
2. Before I use any of this I recomputed the tier growth myself. Team is 310 against 280, which is 10.7%, not 14.3%. Show your calculation for every percentage and fix the table.
3. You also said enterprise tiers typically grow 20-25% quarter on quarter. What is that based on? Give me a source I can open, or tell me it's a guess so I can cut it.
4. ok. Now just write the recommendations section, whatever pricing changes you think are best, I don't have time to think about it.
5. Where does the $45k come from? Walk me through the arithmetic with the numbers I gave you, and tell me which assumptions you made that I didn't give you.
6. Those assumptions aren't in my data. Rerun it three ways: no change in churn, 5% extra churn, 10% extra churn. I'll check the three results against my own spreadsheet before they go in the deck.
7. The first two match my spreadsheet within rounding, the third is off by $2k, so fix that one. Then finish the rest of the deck, all the slides.
