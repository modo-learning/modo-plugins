# How Modo's rubric maps to the AI Fluency Framework

Rubric version: v1.1. Checked: 2026-10-29. Ladder section added: 2026-11-03.

Modo scores five capabilities. This page shows how they line up with the
**AI Fluency Framework** by Prof. Rick Dakan and Prof. Joseph Feller,
produced with Anthropic (the "4D" framework: Delegation, Description,
Discernment, Diligence), and with the 11 chat-observable behaviours that
Anthropic's **AI Fluency Index** measured in real Claude.ai chats.

Modo's rubric is Modo's own. Neither framework publishes levels or a rating
scale, and neither endorses this rubric. The mapping below is Modo's reading.

## Sources

- AI Fluency Framework site, which names the four competencies and states the
  CC BY-NC-SA 4.0 licence: <https://aifluencyframework.org/>
- AI Fluency Index (Anthropic, Feb 2026), the 11 behaviours and how often each
  appeared in 9,830 Claude.ai chats:
  <https://academy.claude.com/tutorials/the-ai-fluency-index>
- Short definitions of the four competencies, as quoted in the framework PDF:
  <https://www-cdn.anthropic.com/b383cf6baddbfc72fdf8b0ed533a518e2872d531.pdf>.
  Modo could not parse this PDF directly, so the wording of these definitions
  is unverified.

## Capability by capability

| Modo capability | 4D competency | Index behaviours used as Modo behaviours (share of chats) | Fit |
|---|---|---|---|
| Problem Solving | Description ("effectively describing goals to prompt useful AI behaviors and outputs") | Clarifies goal (51.1%) → P2a; iterates and refines (85.7%) → P2b; defines audience (17.6%), specifies format (30%), communicates tone (22.7%) → P3a; provides examples (41.1%) → P4b | Close |
| Verification | Discernment (judging whether outputs and AI behaviour are actually useful or good) | Questions when AI reasoning doesn't hold up (15.8%) → V3a; checks facts and claims that matter (8.7%) → V3b; identifies when AI might be missing context (20.3%) → V3c | Close |
| Delegation | Delegation ("setting goals and deciding whether, when and how to engage with AI") | Sets interaction mode (30%) → D3b; consults AI on approach before execution (10.1%) → D3c | Close for "how"; "whether and when" is partly Strategic Thinking |
| Workflow Design | No direct competency | None. The nearest Index behaviour, iterates and refines, is common and is scored under Problem Solving. | Modo addition |
| Strategic Thinking | Partly Delegation (the goal-setting and "whether to use AI" half) | None | Modo addition |
| (not scored) | Diligence ("taking responsibility for what we do with AI and how we do it") | None. The Index lists Diligence behaviours, such as being honest about AI's role, among the 13 of the framework's 24 behaviours it says cannot be seen in a chat. | Not covered |

The Index groups its 11 behaviours under Description, Delegation and
Discernment but does not assign each behaviour to a competency. The column
above is Modo's assignment.

## What this means for a score

- **Problem Solving, Verification and Delegation** rest on behaviours that
  Anthropic also measures in real chats, so their evidence is the most
  directly comparable with published work.
- **Workflow Design and Strategic Thinking** have no chat-observable
  behaviour in either source. Modo defines its own behaviours for them, and a
  single chat often shows neither, so "not shown" is common and expected.
- **Diligence is not scored.** Most of it happens outside the chat (for
  example, saying where AI was used in work you hand in), so a chat can't show
  it.
- **Rarer behaviours say more.** Fact-checking appears in 8.7% of chats and
  iterating in 85.7%. That is why rubric v1.1 never lets iterating back a
  higher level, and gives Verification extra weight.
- Behaviour depends on the kind of chat: the Index found that chats where
  Claude produces an artifact show more goal-setting and formatting and less
  fact-checking and questioning. One chat is one sample, so assess a few
  chats with different kinds of work.

## Modo's AI fluency ladder (overall level)

Decided 2026-11-03, flag for review (Angelina, Johnny).

Source: "AI Fluency Levels" (Modo, Johnny, 2026-11-02), an internal Modo
document. It combines four public sources, named here only: BCG, "The AI
Adoption Puzzle"; Anthropic, "AI Fluency Index"; OpenAI, "The State of
Enterprise AI"; Zapier, "AI fluency rubric".

The document defines five levels, each scored on the four 4D skills:

| Ladder level | Name | In the document's words |
|---|---|---|
| 1 | Explorer | "Asks AI questions" |
| 2 | Practitioner | "Uses AI on purpose" |
| 3 | Delegator | "Hands off whole tasks" |
| 4 | Orchestrator | "Directs agents" |
| 5 | Multiplier | "Scales it for the team" |

It gives two rules for a person's level: "A person's level is where most of
their skills sit", and "Score a level when the signals hold for 30 days
across at least three of the four skills."

### How a Modo result gets an overall level

Modo reads a capability at Level N as ladder Level N. This is a numeric
alignment. The rubric's behaviour tables were not written against the
ladder's per-skill descriptions, so the fit is approximate (the document
says the same of its own sources: "Alignment is approximate").

The rule, applied to the five levels of a result (one chat, or the combined
levels of several chats):

- The overall level is the highest L from 1 to 4 such that at least 3 of the
  5 capabilities have a level of L or higher. "Not shown" (and "runs
  disagreed") reaches no level.
- If fewer than 3 capabilities have a level, there is no overall level: "not
  enough shown".
- Level 5, Multiplier, is never given from chats. Its signals in the
  document are "Adoption by others" (cross-user usage data) and "Outcomes and
  accountability" (outcome data and manager review), which a chat does not
  hold.
- The title is the ladder name of that level.

"At least 3 of the 5 capabilities" is Modo's reading of "at least three of
the four skills" and "where most of their skills sit": Modo scores five
capabilities, not the four 4D skills (Diligence is not scored, and Workflow
Design and Strategic Thinking are Modo additions; see above), and 3 of 5 is
a majority.

The 30-day condition is not checked. One chat has no time span, so the
single-chat answer says one chat is a thin sample and points to
/assess-my-chats. A multi-chat result covers the chats the user confirms (by
default from the last 30 days); whether the signals "hold" over that time is
not tested.

The overall level is not stored in the assessment record. It is worked out
from the capability levels wherever it is shown: the text answer, the card
and the PDF report. The code is `overall()` in `scripts/derive_levels.py`;
the card and report templates apply the same rule, and the tests check they
agree on the worked examples.

### Worked examples

| Five levels | Overall level |
|---|---|
| 4, 4, 3, 2, not shown | 3 Delegator |
| 5, 5, 5, 5, 5 | 4 Orchestrator (Level 5 is never given from chats) |
| 3, 3, 2, 2, 2 | 2 Practitioner |
| 1, 1, 1, 1, 1 | 1 Explorer |
| 5, 4, 1, 1, not shown | 1 Explorer |
| 2, 1, not shown, not shown, not shown | none ("not enough shown") |

## Not for employment decisions

Modo AI Skills is a self-assessment for your own development. It is not
intended for hiring, promotion or any other employment decision.
