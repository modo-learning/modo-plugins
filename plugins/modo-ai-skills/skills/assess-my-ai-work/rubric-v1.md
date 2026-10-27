# Modo AI Skills rubric

**Rubric version: v1**

This is the public rubric behind every Modo AI Skills assessment. Claude reads
this file to score a chat, so what you read here is exactly what is applied.
Every result is labelled "Self-assessment by Claude using Modo rubric v1 — not
verified."

## How scoring works

- The unit is **one chat**. The score describes what the user did in that
  chat, not how good they are in general.
- Only the **user's own messages** count as evidence. What Claude wrote is
  context for understanding them, never evidence of the user's skill.
- Each of the five capabilities gets a **level from 1 to 5**, or **not shown**.
- Each score has a **confidence** (low, medium or high) and **one or two short
  quotes** from the user's messages.
- A chat needs **at least 4 messages from the user** to be scored. Shorter chats
  get a "too short to judge" message and no scores.

### Choosing a level

1. Find the user's moments that bear on the capability.
2. Give the **highest level whose description those moments meet**. A level is
   met only if the user's own words or actions show it, and a quote can be
   pointed to.
3. If the user showed a higher level once but did the opposite at most other
   moments, use the level that fits most of the chat and set confidence to
   **low**.
4. Levels are not cumulative checklists. A level 4 does not need every
   behaviour in level 3, but it does need the behaviours listed for level 4 to
   be visible.

### Not shown

Use **not shown** when nothing in the user's messages bears on the capability,
so any level would be a guess. Missing evidence is not level 1. Level 1 needs
a quotable moment where the low-level behaviour appears. Doing small,
well-specified tasks is not itself low-level behaviour in a capability: when a
chat is only mechanical tasks with no goal, choice, trade-off or handoff in the
user's words, Strategic Thinking is not shown.

### Confidence

| Confidence | Meaning |
|---|---|
| **high** | The level is supported by at least three separate moments in different parts of the chat, and none points to a different level. Not given for a chat with fewer than 6 user messages. |
| **medium** | Supported by two separate moments, or by one clear, sustained exchange over several messages. Moments may differ by at most one level. |
| **low** | Supported by a single moment, or the moments point to levels more than one apart. |

### Level to 0-100 bands

Used only where a 0-100 display is needed (such as a ring on a card). The text
result shows the level, not a number out of 100.

| Level | Band | Shown as |
|---|---|---|
| 1 | 0-20 | 10 |
| 2 | 21-40 | 30 |
| 3 | 41-60 | 50 |
| 4 | 61-80 | 70 |
| 5 | 81-100 | 90 |
| not shown | no score | no ring |

A band is a range of possible values; the "shown as" value is its midpoint and
is what a card displays. Nothing finer than a level is claimed.

---

## 1. Problem Solving

Framing the problem, giving Claude what it needs, and adjusting when it does
not work.

| Level | What the user's messages show |
|---|---|
| 1 | Asks a bare question or command with no goal, context or constraints ("write a report"). Accepts the first answer or repeats the same request unchanged. |
| 2 | States a goal but leaves out who it is for, the situation or the limits. When the answer misses, rewords the same request instead of saying what was wrong. |
| 3 | Gives the goal plus relevant context up front (audience, existing material, format). Follow-ups name specific gaps ("the second paragraph ignores the budget"). |
| 4 | Breaks a messy problem into parts or an order of steps, states constraints and what a good answer looks like, supplies examples or data. When an attempt fails, says why and changes the approach. |
| 5 | Questions or reframes the problem itself, compares approaches and picks one with stated reasons, sets success criteria before starting, and revises the plan from what each attempt revealed. |

## 2. Verification

Checking what Claude produces before relying on it.

| Level | What the user's messages show |
|---|---|
| 1 | Takes answers as given and builds on them. No questions about whether something is right, even where the answer contains numbers, facts or code. |
| 2 | Reacts only to obvious errors, or asks "are you sure?" without checking anything themselves. |
| 3 | Checks some claims against their own knowledge or a source: spot-checks a figure, asks where a fact comes from, points out a specific discrepancy. |
| 4 | Checks deliberately and more than once: asks for sources or the working, recomputes or runs the result themselves, compares with a second source, and has errors fixed and re-checked. |
| 5 | Builds checking into the work: sets acceptance checks before starting, tests edge cases, verifies with an independent method (a separate calculation, running the code, ground-truth data), and states what has and has not been verified before relying on it. |

## 3. Workflow Design

Structuring multi-step work, and making a process reusable.

| Level | What the user's messages show |
|---|---|
| 1 | Treats each request as a stand-alone question. Re-explains context from scratch each time. |
| 2 | Moves through steps in some order but ad hoc, with no plan stated. Repeats setup when starting the next piece. |
| 3 | Lays out steps in order within the chat (outline, then draft, then revise) and feeds earlier outputs into later steps. |
| 4 | Defines a repeatable process: fixed format or rules, a template, stages with a check between them, applied the same way to several items. |
| 5 | Turns the process into something reusable: asks to save it as a template, prompt or skill, defines inputs and outputs for each stage, and plans for variants and failures. |

## 4. Delegation

Deciding what to hand to Claude and what to keep, and how to hand it over.

| Level | What the user's messages show |
|---|---|
| 1 | Hands over a whole job vaguely ("do my report", "whatever you think is best") with no scope, role or output described, and does not look at it before moving on. |
| 2 | Hands over a whole task with a minimal brief (a topic and perhaps a length). No review point and no decision kept for themselves. |
| 3 | Gives a clear task with scope and output format, and keeps some decisions ("give me three options, I'll choose"). |
| 4 | Splits work on purpose between themselves and Claude. Gives a role, inputs, constraints and what done looks like, and sets a review step before Claude carries on. |
| 5 | Explains why some parts stay human and others are handed off. Each handoff has a full brief and acceptance criteria. Uses separate passes or roles for different jobs and reviews each handoff. |

## 5. Strategic Thinking

Deciding where AI is worth using, and tying the work to a larger goal.

| Level | What the user's messages show |
|---|---|
| 1 | Explicitly leaves the choice of approach or direction to Claude (for example "whatever you think is best") without stating a goal beyond the task. |
| 2 | Mentions the purpose or audience in passing. Does not weigh alternatives or consequences. |
| 3 | Connects the task to a goal beyond the chat (a decision, a deadline, an audience) and uses it to decide what to prioritise. |
| 4 | Weighs options and trade-offs (time, cost, risk, quality) and uses Claude to test the plan: alternatives, counter-arguments, risks. |
| 5 | Places the AI work inside a larger plan: decides which problems are worth AI and which are not, anticipates risks and limits, has Claude challenge their own assumptions, and ties the work to an outcome that can be measured. |

---

## For reviewers

Notes for Angelina's review. Decisions that are not product facts and can be
changed:

- Level 1 requires a quotable low-level moment. "Nothing shown" is not level 1.
- High confidence needs at least 3 moments and at least 6 user messages. These
  thresholds are a judgement call and are not taken from any source.
- The 0-100 bands are equal fifths. The shown-as value is the band midpoint.
- Changing any wording means a new version string (v2); results always record
  the rubric version they used.
