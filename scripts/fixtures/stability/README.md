# Stability golden set (ticket 33)

Fixed chats for the stability test: score the same chat many times and check
the result does not move. `scripts/gen_stability_evals.py` turns them into the
`stab-*` cases in `plugins/modo-ai-skills/evals-stability/`;
`scripts/stability_report.py` compares the runs with the bands below.

Each `<id>/chat.json` holds the chat (`turns`), the behaviours planted in it
(`planted`, as rubric ids per message; our chats only) and `expected`: the
levels each capability may take (`bands`), the accepted titles, whether the chat
is an agent session and a reason for each. `scripts/test_stability_report.py`
checks that the planted behaviours give levels inside the bands under the
published rule.

| Chat | Kind | Typed messages | Planted reading |
| --- | --- | --- | --- |
| strong-verifier | synthetic | 6 | Verification 5; Practitioner |
| weak-delegator | synthetic | 6 | Delegation 2 (unchecked handoffs); Practitioner |
| all-level-1 | synthetic | 6 | every capability 1; Explorer |
| mixed | synthetic | 7 | Workflow 5, Problem Solving 5, Verification 1; no agent, so Delegator |
| borderline | edge case | 5 | Delegation 2 (a minimal brief, rubric v1.2), so Practitioner under Johnny's rule (it sat on the Practitioner/Delegator line before) |
| thin | edge case | 4 | few messages; Workflow Design 2 under rubric v1.2, so Practitioner |
| johnny-e1, -e2 | Johnny's example | 4 | Explorer |
| johnny-p1, -p2 | Johnny's example | 4 | Practitioner |
| johnny-d1, -d2 | Johnny's example | 5 | Delegator (D1 reaches Orchestrator scores with no agent) |
| johnny-o1, -o2 | Johnny's example | 6 | Orchestrator, agent session |
| johnny-edge-fact-check | Johnny's edge case, our chat | 4 | a strong fact-check that shows only 2 capabilities; No title yet |
| johnny-edge-plain-chat | Johnny's edge case, our chat | 6 | a great plain chat with no agent; Delegator |
| johnny-edge-claim | Johnny's edge case, our chat | 4 | "12 people on my team use my agent" is a claim; no agent session |

**Johnny's examples** (credit: Johnny, AI Fluency Levels scoring rules v1,
2026-11-04). The `johnny-*` chats hold his user messages word for word; his file
shows no replies, so Claude's turns are a placeholder. `johnny_scores` are his
scores. `bands` are his scores within 1 (ticket 35, D8), and a capability he
gave no score has no band (not specified). His titles are exact, and they count
as independent of our rule. His edge cases are descriptions, not chats, so the
chats are ours and have no scores. `johnny-edge-claim` has no title in his file:
the two accepted there are ours.

Multi-chat set: our six (`MULTI_SET_CHATS` in `stability_report.py`). Its
expected combined bands are worked out from the chats' bands by the published
combining rule (`aggregate_chats.combine`). With 6 chats there is no person
title, so its expected title line is "6 of 10 chats to your title".

**Source and consent.** Our six are written for this test. Every name, company
and figure is invented, so no consent is needed and nothing was removed.

**Still to add:** 6 real chats, with the owner's consent and personal details
removed (names, emails, companies, identifying numbers). For each, record here
where it came from, who consented and what was removed. Then add them to the
multi-chat set as the ticket asks.

**Status of the bands:** a proposal for our six; Angelina reviews them. Our
six titles were worked out with the rule (Johnny's rule since ticket 35, with no
agent session in any of them), so for the title-method comparison (ticket 33
Part 3b) Angelina writes her own expected titles without seeing these.
