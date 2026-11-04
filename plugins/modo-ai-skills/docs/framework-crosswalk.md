# How Modo's rubric maps to the AI Fluency Framework

Rubric version: v1.1. Checked: 2026-10-29. Titles section updated: 2026-11-04.

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

## Titles: Modo's AI fluency levels

Credit: Johnny, AI Fluency Levels scoring rules v1, 2026-11-04, an internal
Modo document. His rules replaced the rule Modo used before, and they take
priority over it. The five capabilities and rubric v1.1 stay as they are.

The titles come from Modo's AI fluency ladder ("AI Fluency Levels", Modo,
Johnny, 2026-11-02), which draws on four public sources, named here only: BCG,
"The AI Adoption Puzzle"; Anthropic, "AI Fluency Index"; OpenAI, "The State of
Enterprise AI"; Zapier, "AI fluency rubric".

### The title for one chat

Give the highest title whose rule is met.

| Title | Rule |
|---|---|
| Orchestrator · Level 4 | 3 of 5 capabilities at 4+, including Delegation. The user must be directing an agent or tools. |
| Delegator · Level 3 | 3 of 5 capabilities at 3+, including Delegation |
| Practitioner · Level 2 | 3 of 5 capabilities at 2+ |
| Explorer · Level 1 | 3 of 5 capabilities shown at any level |
| No title yet | Fewer than 3 capabilities shown |

Delegation is required at Levels 3 and 4 because those titles are about handing
work to AI. Multiplier, Level 5, comes later: once people can share how they
use AI on Modo, it means an Orchestrator whose shared workflows other people
regularly reuse. A claim in a chat is not evidence.

Scores that reach Orchestrator with no agent session give Delegator, with the
note "no agent work visible in this chat". "Not shown" and "runs disagreed"
reach no level.

The same rule runs on every surface. The code is `overall()` in
`scripts/derive_levels.py`; the card and report templates apply the same rule,
and the tests check they agree on every set of levels and on Johnny's examples.

### The title for a person

This is Claude multi-chat only, worked out inside one /assess-my-chats run from
the chats in that run. Nothing is stored, and nothing here is in the assessment
record.

- **Proven level per capability:** the highest level reached in at least 3
  chats. The median stays the main level.
- **Your title:** the highest chat title reached in at least 3 chats, shown once
  there are 10 scored chats. Before that the result says "N of 10 chats to your
  title". A scored chat with no title counts toward the 10 but adds no title
  toward the 3 chats.
- **Task range:** how many of the 8 task types the chats cover (Writing and
  editing, Research and summarizing, Data analysis, Coding, Planning and
  decisions, Brainstorming, Learning, Operations and admin). Each chat gets
  exactly one, the closest match.
- **Reuse:** how many chats used saved work: a skill or slash command, a pasted
  or named saved prompt or template, a project with saved instructions, or "use
  my usual format". Counts only, with no saved-prompt names.

### Readings pending Johnny's answer

Johnny's file leaves these open. Modo reads them this way until he answers:

- **Agent session** (his "directing an agent or tools"): at least 2 tool-driven
  steps with the user directing or reviewing them, on any surface. One web
  search doesn't count. Evidence is tool names or the user's own messages, and
  most of the 3 to 5 scoring runs decide. No evidence means no.
- **"Reached in at least 3 chats" is cumulative:** a higher chat title also
  counts toward lower ones, and the same goes for Proven level. His example
  (Delegator in 3 chats, Practitioner in 6, Explorer in 3) reads the same either
  way.
- **Proven level replaces Best shown** for people, and the median stays the main
  level. His file doesn't say which of them leads. The record keeps `best_shown`
  unchanged.

In v1 nothing expires, by his rules. A run only sees the chats in it, because
the stored score sheet needs the backend. Not specified: how a stored sheet will
treat chats counted twice.

## Not for employment decisions

Modo AI Skills is a self-assessment for your own development. It is not
intended for hiring, promotion or any other employment decision.
