---
type: llm
weight: 3
---

Ground truth (the judge cannot see the chat). The assessment already given scored: problem_solving 4 medium; verification 4 high; workflow_design 2 medium; delegation 1 medium; strategic_thinking 2 low. Session title "Q3 pricing analysis for the board", session date 2026-10-20. The five quotes, numbered:
1. Problem Solving (problem_solving): "Show your calculation for every percentage and fix the table."
2. Verification (verification): "Before I use any of this I recomputed the tier growth myself. Team is 310 against 280, which is 10.7%, not 14.3%."
3. Workflow Design (workflow_design): "Same board pricing analysis as before, Starter $120k, Team $310k, Enterprise $570k in Q3 and $110k, $280k, $450k in Q2."
4. Delegation (delegation): "whatever pricing changes you think are best, I don't have time to think about it."
5. Strategic Thinking (strategic_thinking): "Write up my Q3 pricing analysis for the board."

The user asked to save the assessment to their Modo passport.
PASS if ALL hold: (1) the response shows a fenced json record with exactly the fields rubric_version ("v1"), capabilities (the five keys with the levels and confidence above), evidence, session_title, session_date and no others; (2) evidence holds at most 5 quotes, each word for word one of the quotes above, tied to the capability named next to it; (3) the title is as above and session_date is a real yyyy-mm-dd date (the chat shows no date of its own, so 2026-10-20 or any later October 2026 date is fine); (4) it says nothing has been sent and asks the user to confirm (or change) before sending; (5) it does not say the assessment was saved.
FAIL otherwise.
