# Stability golden set (ticket 33)

Fixed chats for the stability test: score the same chat many times and check
the result does not move. `scripts/gen_stability_evals.py` turns them into the
`stab-*` cases in `plugins/modo-ai-skills/evals-stability/`;
`scripts/stability_report.py` compares the runs with the bands below.

Each `<id>/chat.json` holds the chat (`turns`), the behaviours planted in it
(`planted`, as rubric ids per message) and `expected`: the levels each
capability may take (`bands`), the accepted overall titles and a reason for
each. `scripts/test_stability_report.py` checks that the planted behaviours
give levels inside the bands under the published rule.

| Chat | Kind | Typed messages | Planted reading |
| --- | --- | --- | --- |
| strong-verifier | synthetic | 6 | Verification 5; Practitioner |
| weak-delegator | synthetic | 6 | Delegation 2 (unchecked handoffs); Practitioner |
| all-level-1 | synthetic | 6 | every capability 1; Explorer |
| mixed | synthetic | 7 | Workflow 5, Problem Solving 5, Verification 1; Orchestrator |
| borderline | edge case | 5 | one level from Practitioner/Delegator on purpose |
| thin | edge case | 4 | few messages; Practitioner or not enough shown |

Multi-chat set: all six (`MULTI_SET_CHATS` in `stability_report.py`). Its
expected combined bands are worked out from the chats' bands by the published
combining rule (`aggregate_chats.combine`).

**Source and consent.** All six are written for this test. Every name, company
and figure is invented, so no consent is needed and nothing was removed.

**Still to add:** 6 real chats, with the owner's consent and personal details
removed (names, emails, companies, identifying numbers). For each, record here
where it came from, who consented and what was removed. Then add them to the
multi-chat set as the ticket asks.

**Status of the bands:** a proposal. Angelina reviews them. The titles here
were worked out with the rule, so for the title-method comparison (ticket 33
Part 3b) Angelina writes her own expected titles without seeing these.
