---
type: llm
weight: 2
---

Each repeated task should have exactly one suggested fix.

PASS if all of these hold: the Xero expense item says a connector (Xero) is needed first; the investor update item says it is already covered by the existing investor-update skill (a tweak may be suggested); the Acme status report item suggests a scheduled task or a skill (either is acceptable, since it needs notes the user pastes in); the outreach item suggests a skill.
An item may mention a later upgrade after its main fix (for example "a scheduled task could come later"); that still counts as one fix.
FAIL if any of these items has a different main fix type, or an item hedges between fix types without committing to one.
