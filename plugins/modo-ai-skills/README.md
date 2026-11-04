# Modo AI Skills

Modo AI Skills tells you how well you work with AI, from one Claude chat you
choose or from several of your past claude.ai chats at once, against Modo's
public rubric. For each of five capabilities (Problem
Solving, Verification, Workflow Design, Delegation, Strategic Thinking) you
get a level from 1 to 5, or "not shown", a confidence label, a quote from your
own messages as evidence, and what the next level looks like. Then it gives
you two concrete improvements for your weakest areas, each with a prompt to
try next time.

**Not for hiring or employment decisions.** Modo AI Skills is a
self-assessment for your own development. It is not intended for hiring,
promotion, performance reviews or any other employment decision about you or
anyone else.

This version (0.5.0) carries **rubric v1.1**: scoring prompt by prompt against
published behaviours, a fixed level rule, 3 to 5 scoring runs with their
agreement shown, honest coverage for thin chats, and a redesigned card. New
in 0.5.0: [titles](#titles) by Johnny's AI Fluency Levels scoring rules v1, with
a title for each chat and, across 10 scored chats, one for you.
See [What changed in v1.1](#what-changed-in-v11).

It's made for people who use Claude every day for real work and want honest
feedback on how they frame problems, check Claude's work, build repeatable
workflows, hand work over and decide where AI is worth using, with something
concrete to keep.

## What you get

- **A level for each capability**, written as "Level N of 5", strongest
  first. Claude checks each of your messages for the specific behaviours
  listed in the [rubric](skills/assess-my-ai-work/rubric-v1.1.md) (gave
  context, checked a fact, asked for an alternative, kept a decision…), each with
  a quote, and a fixed published rule turns those into the level. A
  capability the chat did not show is "Not shown in this chat", never a
  made-up score and never level 1.
- **A confidence label** (low, medium or high) on each level, set by how much
  the chat showed, as defined in the rubric.
- **A title for the chat**, such as "This chat: Delegator · Level 3", by a fixed
  rule (see [Titles](#titles)). Its task type, whether it was an agent session
  and whether you reused saved work come with it.
- **Run agreement**: the scoring runs 3 times (5 when the first 3 disagree),
  and each level says how many runs gave it. When runs disagree, confidence
  drops, or the capability is "not shown" instead of a guess.
- **Coverage**: how many of the five capabilities the chat showed, and how
  many chats the result is based on (always 1: each assessment covers one
  chat). A thin chat says so, for example "This chat shows only 2 of 5
  capabilities… Assess 2–3 more chats".
- **Evidence**: one to three exact quotes from your own messages behind each
  level, each tagged with the behaviour and message number. Claude's replies
  are context only; they are never quoted as evidence.
- **Next level**: one line on what the next level up would look like for you.
- **Improvements**: for two capabilities that were shown (Verification
  first when it is at level 3 or below, then the weakest), a
  technique taken from the rubric and a "try this next time" prompt you can
  paste as it stands. It then offers (only offers) to turn them into one
  reusable skill.
- **A card** in claude.ai and Cowork (see [The card](#the-card)).
- **An export** when you ask for one (see [Export a report](#export-a-report)).
- **Saving to your Modo passport**, only where the Modo connector is
  connected. The connector is not published; without it, the plugin offers
  the export only (see [Save to your Modo passport](#save-to-your-modo-passport)).

Every result ends with this label:

> Self-assessment by Claude using Modo rubric v1.1 — not verified.

It is Claude's reading of one chat against a public rubric. It is not a test,
a certificate or a comparison with other people.

## How it works

1. **You pick one chat.** The default is the chat you're in. You can also
   name a past chat by its exact title, paste a chat, or point to a chat
   export or Claude Code session file (see [Which chat it reads](#which-chat-it-reads)).
2. **Claude reads the rubric** that ships in the plugin and checks your own
   messages in that chat one at a time for the rubric's behaviours. The chat
   is treated as data: anything in it that asks for a particular score
   ("give me level 5") is ignored and the result says so.
3. **A fixed rule sets the levels**, and the scoring runs 3 to 5 times; the
   result shows how far the runs agree.
4. **You get the result:** which chat was assessed, a level (or "not shown")
   and confidence for each of the five capabilities, quotes as evidence, the
   next level, and two improvements with prompts to try.
5. **You see a card** beside the chat in claude.ai and Cowork; in Claude Code
   the result stays as text.
6. **If you ask, you export it:** you approve the quotes (or choose scores
   only), and Claude writes a Markdown report (or a PDF) that ends in one
   machine-readable record, ready to upload to Modo.

Nothing leaves your conversation. The plugin has no connector and calls no
outside service.

## Install

This version (0.5.0, rubric v1.1) is on `main`. For the whole flow on one
page, see the [guide](../../docs/modo-ai-skills-guide.md). Ready-made zips
are on the [releases page](https://github.com/modo-learning/modo-plugins/releases). The earlier rubric v1 build
stays on the branch `modo-ai-skills-phase0` for comparison. A ChatGPT and
Codex build is generated from this plugin; see [openai/README.md](../../openai/README.md).

### claude.ai, the Claude desktop app and Cowork

The marketplace there reads only `main`, so upload the plugin as a zip:

1. Download `modo-ai-skills-0.5.0-claude.zip` from the
   [releases page](https://github.com/modo-learning/modo-plugins/releases),
   or build it from a clone as below (the older v0.1.0 test build there is
   rubric v1). Don't use GitHub's "Download ZIP" for the whole repository:
   it holds two plugins, and the upload takes one.

   ```
   git fetch origin main
   git archive --format=zip -o modo-ai-skills.zip origin/main:plugins/modo-ai-skills -- . ':!evals' ':!evals-stability'
   ```

2. Open **Customize → Plugins → Add → Upload plugin** and choose the zip.
3. To assess a past chat by its title, or several past chats at once, turn on
   **Settings → Memory → "Search and reference chats"**.
4. Start a new chat, work on something real for at least 4 messages, then ask
   "how good am I at using AI in this chat?", and then "export it".

To update, remove the plugin in Customize → Plugins and upload the new zip.

### Claude Code

```
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-ai-skills@modo-plugins
```

If you added `modo-plugins` from a branch before, remove it and add it again
from `main` (this also reinstalls Task Finder):

```
claude plugin marketplace remove modo-plugins
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-ai-skills@modo-plugins
claude plugin install modo-task-finder@modo-plugins
```

Assessing several past chats needs claude.ai's chat tools, so it works in
claude.ai and the desktop app, not in Claude Code.

To update: `claude plugin marketplace update modo-plugins`, then
`claude plugin update modo-ai-skills@modo-plugins`.

## How to ask

In Claude chat or Cowork, ask in plain words, for example:

- "How good am I at using AI?"
- "Assess this chat."
- "How good am I at working with AI across my recent chats?" (several chats)
- 'Assess my chat called "Q3 budget review".'
- "How do I get better at verification?"
- "Export this assessment."
- "Save this to my Modo passport." (only with the Modo connector)

Or run the skills by name. In Claude Code, and from the `/` menu in the Claude
app:

| Command | What it does |
|---|---|
| `/modo-ai-skills:assess-my-ai-work` | Assess one chat |
| `/modo-ai-skills:assess-my-chats` | Assess several past claude.ai chats at once (claude.ai and desktop only) |
| `/modo-ai-skills:help-me-improve` | Help with one capability, without an assessment |
| `/modo-ai-skills:export-assessment` | Export the assessment you were just given |
| `/modo-ai-skills:save-to-passport` | Save the assessment to your Modo passport, or show the passport (needs the Modo connector) |

## Assess several chats at once

`assess-my-chats` scores up to 25 of your past claude.ai chats (by default
the 15 newest from the last 30 days) and combines them into one result.

1. It lists the chats it would read, by title and date, and reads nothing
   until you say yes. You can untick chats by number, change the date range
   or the number of chats. Incognito chats are never listed; chats flagged by
   the safety classifier and empty chats are skipped and counted.
2. Each chat is read and scored by its own agent, 5 at a time, with the same
   rubric and the same 3 to 5 scoring runs as a single chat. The main chat
   only receives each chat's levels, quotes and coverage, never the
   transcript. Chats with fewer than 4 typed messages are counted as too short.
3. For each capability, the level is the middle of the chat levels (the lower
   one on a tie). You also see your Proven level (the highest level reached in
   at least 3 chats), how many chats show it, a confidence label from how close
   the levels are, and a trend (older against newer chats, with 4 or more
   chats).
4. Each chat gets its own title. From 10 scored chats you get [your title](#titles);
   before that the result says "8 of 10 chats to your title". You also see your
   task range ("Task range: 5 of 8 types") and reuse ("Reused saved work: 3 of 8
   chats"), as counts only.
5. You get one card ("Based on N chats, date range"), a table with a row per
   chat and its title, and a coverage line naming what could not be read
   (attachments, tool results, answers picked in Claude's question widgets).

Export works as for one chat: you approve every quote, and chat titles are
left out ("Chat 1…N") unless you say "with titles". Saving a multi-chat
result to the Modo passport needs a Modo connector that accepts results
across several chats; until then the skill says so and sends nothing.

## Which chat it reads

It assesses **exactly one chat: the one you pick**. It never browses, lists,
skims or searches your other chats, and never looks around your computer for
files or logs. If you ask for "all my chats" or an overall picture, it says
it assesses one chat at a time and assesses the current one.

The first line of the result always says which chat or file was assessed. A
chat needs at least 4 messages from you; with fewer it says the chat is too
short to judge (and gives the count) instead of giving scores.

You choose the chat in one of these ways:

- **The chat you're in** (the default). It reads the messages in this chat
  before your request to assess it.
- **Pasted text.** Paste the chat into your message. Your messages are the
  parts labelled as yours ("You", "Me", "User", "Human" or similar). If it
  can't tell which parts are yours, it asks.
- **A chat you name.** Give the chat's **exact title**, for example
  `assess my chat "Q3 budget review"`. It looks the chat up by that title
  only, with Claude's own past-chat tools in the app you are using:
  - With a tool that opens a chat by its title, it opens that one chat.
  - If the only tool is a search, it runs one search with your exact title
    and considers only results whose title is that title (letter case aside).
    It never reads, shows, lists or uses any other result, and doesn't search
    again with other words.
  - If several chats have that title, it asks "which one?", listing only those
    chats (title and date), and never picks for you.
  - If no chat has that title, it says so without describing anything else
    the search returned, and offers two ways forward: paste the chat or point
    to a chat export file.
  - If the app has no way to open past chats (Claude Code, for example), it
    says so and offers: paste the chat, point to a chat export file, or run
    the assessment inside that chat.
  - It never scores a chat it hasn't opened.
- **A chat export file.** Point to the file by its path (for example
  `conversations.json` from your Claude data export). It reads only that file
  and only the chat inside it that you name (or its only chat, if it holds
  one). If the file holds several chats and you name none, it asks which
  one, listing their titles and dates. If the file can't be read, it says so and asks for the right path or the chat
  pasted; it doesn't search for the file. Tested with exports where each chat
  has a title, a date and messages whose sender is `human` or `assistant`;
  other export shapes are not specified.
- **A Claude Code session file**, only if you point to it. Give the path of
  the session `.jsonl` file. It counts only the lines you typed; tool output
  that Claude Code stores as "user" lines is never counted or quoted. It never
  mentions or offers session files or other coding-tool logs unless you point
  to one yourself.

## The card

In claude.ai and Cowork, when Claude can create an artifact, the result is
also shown as an **AI capability card** beside the chat. It leads with your
strongest capability under a title line ("This chat: Delegator · Level 3"),
then shows one row per capability, strongest first:
five segments filled to the level, the confidence (as a label and as the fill:
solid for high, lighter for medium, striped for low) and how many scoring runs
agreed. A capability that was not shown is a dashed empty track marked "Not
shown in this chat", listed last and never a zero. Below that: the coverage
line, "Based on 1 chat", one or two quotes from your strengths, one growth tip
and one next action, then the label. The card holds nothing that
isn't in the text result, is not saved anywhere else, and makes no network
calls.

In Claude Code the result stays plain text and there is no card. Samples:
[dark](docs/passport-card-sample.png) and
[light](docs/passport-card-sample-light.png).

The card and the PDF report share one look, the Modo app's: a navy header,
Modo yellow as the accent, warm neutral surfaces and Inter, in a card layout
close to shadcn/ui. The style lives in the `modo-design` skill
([skills/modo-design/](skills/modo-design/SKILL.md)): one tokens file and the
component rules. It is plain HTML and CSS, with no framework and no network
calls; if Inter isn't installed, the system font is used.

## Improvements and the skill offer

After the five levels, the assessment picks two capabilities that were shown
(Verification first when it is at level 3 or below, because checking Claude's
work carries extra weight; then the weakest; the only one, if just one was
shown; never a "not shown" one) and gives each a technique from the rubric and
a prompt to try next time. A "Next step" line follows: assess more chats when
coverage is thin, otherwise try the first prompt in your next chat. It then asks whether you want them
turned into one reusable skill. Nothing is saved unless you choose:

- In the Claude app, the skill appears as a **Save skill** card that you save
  or dismiss.
- Otherwise it uses a skill-creator skill if you have one, or writes the
  complete skill in the chat for you to save from Claude's skills settings.

To work on one capability without an assessment, ask "how do I get better at
delegating?" or run `/modo-ai-skills:help-me-improve`. That skill reads no
chat, file or log, gives no level or score, and carries no self-assessment
label, because it assesses nothing.

## Export a report

After an assessment, ask "export this" or run
`/modo-ai-skills:export-assessment`.

1. Claude proposes what would go in: up to 5 of the evidence quotes the
   assessment already showed (each tied to a capability that has a level, each
   checked word for word against your messages), a title and a date. Nothing
   is written yet.
2. You decide: keep them, drop quotes by number, change the title or date, or
   say "scores only" for no quotes at all. A dropped quote appears nowhere.
3. Claude shows the complete report, exactly as it would be saved.
4. Nothing is written until you ask. If Claude can create files in your
   session, say "save it" and it saves `modo-assessment-<date>.md` in the
   current folder (or a name and place you give). If it can't, the report in
   the chat is the export, for you to copy into a `.md` file. A PDF is made
   only if you ask for one, and only if Claude can create files in your
   session. It uses the Modo report template, so it looks like the card
   ([sample](docs/report-sample.png)).

**What the export contains, and nothing else:** the rubric version, the five
levels and confidence labels, the quotes you approved, the session title and
the session date, plus fixed explanatory text and the label. The title is at
most 120 characters: the chat's own title when it has one, otherwise a short
description of the subject that leaves out names of people, companies, email
addresses and amounts. You can change the title and date before anything is
written. The report never contains the chat, a summary or
paraphrase of it, Claude's replies, the next-level notes, the improvements or
the prompts.

The report ends with one machine-readable block holding exactly those fields.
Its exact shape and limits (at most 5 quotes of at most 240 characters each,
for example) are in
[skills/export-assessment/RECORD.md](skills/export-assessment/RECORD.md).

The plugin never uploads the report. You upload it to Modo yourself. Which
file the Modo upload page accepts is not specified yet; until it is, the
export is the Markdown report, and a PDF on request.

## Save to your Modo passport

Saving needs the **Modo connector**, which is not published; without it, the
plugin offers export only. The plugin ships without a connector entry, and
saving is offered only in a session where the connector has been added.
Claude recognises the connector by its tools, `save_assessment` and
`get_passport`, whatever name the connector was added under.

- **Without the connector** nothing changes: the assessment ends by offering
  the export only. If you ask to save to your Modo passport, Claude says the
  Modo connector isn't connected in this session and offers the export
  instead.
- **With the connector**, the assessment's last sentence also says you can ask
  to save it to your Modo passport. Nothing is sent unless you ask.

When you ask ("save this to my Modo passport" or
`/modo-ai-skills:save-to-passport`):

1. Claude shows **exactly the record it would send**: the quotes it proposes,
   numbered, and the record itself as JSON (rubric version, the five levels
   and confidence labels, the quotes, the session title and the session
   date). The quotes, title and date are chosen the same way as for an
   export. Nothing has been sent yet.
2. You decide: say "send it", drop quotes by number, say "scores only" for no
   quotes, change the title or date, or say no. **After any change Claude
   shows the whole updated record again and waits for your yes**, even if you
   said "drop quote 4 and save it". A "no", or anything that isn't a clear
   yes, sends nothing.
3. Only after your yes does Claude call `save_assessment`, once, with exactly
   the record you saw. Claude's own tool-approval prompt, if your app shows
   one, is a second check.
4. Claude says it was saved (with the title and date the server returned) and
   asks whether you want to see your passport.

If the server rejects the record, Claude says nothing was saved and what the
server said. It does not send it again on its own and never changes the
record to get it accepted (for example to another rubric version). If a
change you can make would fix it, such as dropping a quote, it shows the new
record for your yes. If the server could not store the record, Claude says
you can try again later and offers the export; otherwise it offers the export.

**Your passport.** Ask "show my Modo passport" (or say yes after a save).
Claude calls `get_passport` and shows the latest level and confidence for
each capability and your saved assessments, newest first, with their titles,
dates and levels. The passport does not return your quotes.

**What is sent, and nothing else:** the same record as the export's
machine-readable block, described in
[skills/save-to-passport/RECORD.md](skills/save-to-passport/RECORD.md):
`rubric_version`, the five `capabilities` (level and confidence), `evidence`
(the quotes you approved, at most 5, each at most 240 characters; empty for
scores only), `session_title` (at most 120 characters) and `session_date`. It
never sends the chat, a summary, Claude's replies, the next-level notes, the
improvements or the prompts.

## What it reads, what it sends, and your privacy

- **What it reads:** only the one chat you pick, in one of the ways above. For
  an export or a save, it reads the assessment already in your conversation and, to
  check your quotes, the chat that was assessed. It does not read any other
  chat or file.
- **What it never does:** browse or search your chat history, list your
  chats, look for files or logs on your computer, or mention coding-tool
  session logs unless you point to one.
- **What it sends:** nothing, unless the Modo connector is connected and you
  say yes to saving: then exactly the record you were shown goes to your
  Modo passport, and nothing else (see
  [Save to your Modo passport](#save-to-your-modo-passport)). Apart from that
  it calls no outside service. No transcript and no other chat is ever sent
  anywhere. Where Claude can start its own sub-tasks (subagents in Claude
  Code), the repeated scoring runs may each be a sub-task inside your session;
  each gets only the rubric and your messages from the chat you picked.
- **What it writes:** nothing, unless you ask. The only exceptions are the
  card in claude.ai and Cowork (shown beside the chat), a skill you choose to
  save, and an export file you ask for.
- **Saving to Modo:** only through the Modo connector, which is not
  published yet, and only after you have seen the exact record and said yes.

The plugin is a set of instructions for Claude, plus two templates in Modo's
style, the card and the PDF report (HTML pages whose small scripts lay out the
result and make no network calls). It
contains no connectors and no background processes. You can read all of it
in the `skills/` folder.

## Titles

Credit: Johnny, AI Fluency Levels scoring rules v1. Each chat gets the highest
title whose rule is met:

| Title | Rule |
|---|---|
| Orchestrator · Level 4 | at least 3 of your 5 capabilities at Level 4 or higher, including Delegation, and you directed an agent or tools |
| Delegator · Level 3 | at least 3 at Level 3 or higher, including Delegation |
| Practitioner · Level 2 | at least 3 at Level 2 or higher |
| Explorer · Level 1 | at least 3 shown, at any level |
| No title yet | fewer than 3 shown |

Scores that reach Orchestrator with no agent session give Delegator, with the
note "no agent work visible in this chat". An agent session is at least 2
tool-driven steps that you direct or review, on any surface; one web search
doesn't count. Multiplier, Level 5, comes later: it needs Modo sharing data, and
a claim in a chat is not evidence.

**Your title** is the highest chat title you reached in at least 3 chats, shown
once 10 chats are scored. It takes `assess-my-chats`, and it comes from the chats
in that run: nothing is stored. A single chat says "One chat is a thin sample:
your title comes from 10 scored chats."

The title is worked out from the levels wherever it is shown (the text, the
card, the Markdown and PDF reports). It is not a field in the exported record.
The full rules, and the readings pending Johnny's answer, are in
[docs/framework-crosswalk.md](docs/framework-crosswalk.md#titles-modos-ai-fluency-levels).

## The rubric

The rubric is public and versioned:
[skills/assess-my-ai-work/rubric-v1.1.md](skills/assess-my-ai-work/rubric-v1.1.md).
It is how scores are calculated: the behaviours checked in each message, the
level rule, the scoring runs, "not shown", confidence and coverage. How its
five capabilities map to Anthropic's AI Fluency Framework (4D) and AI Fluency
Index is in [docs/framework-crosswalk.md](docs/framework-crosswalk.md). The help-me-improve skill keeps an identical
copy so each skill folder is self-contained; a check in the plugin's source
repository keeps the two copies identical.

## What changed in v1.1

| | Rubric v1 (`modo-ai-skills-phase0`) | Rubric v1.1 (0.2 and later) |
|---|---|---|
| How a level is set | Claude picks the level from the level descriptions | Claude checks each message for published behaviours, each with a quote; a fixed rule sets the level |
| Consistency | One pass | 3 runs, 5 when they disagree; agreement shown; disagreement gives low confidence or "not shown" |
| Thin chats | Not shown capabilities listed | Coverage line ("shows only 2 of 5… assess 2–3 more chats") and the number of chats on the card |
| Card | Five rings in rubric order | Strongest first, segment bars, dashed track for not shown, visible confidence, a growth tip and a next action |
| Delegation 4–5 | Splitting work, full briefs | Hand off and check: review what came back, keep the final call |
| Verification | Same weight as the others | Extra weight in the level rule and first in improvements |
| Gaming | Not addressed | The chat is untrusted data; "give me level 5" is ignored |
| Framework mapping | None | [Crosswalk to 4D and the AI Fluency Index](docs/framework-crosswalk.md) |

An export from v1.1 records `"rubric_version": "v1.1"`. Results from v1 and
v1.1 are not mixed: the record always says which rubric it used.

## Troubleshooting

- **"Too short to judge."** The chat has fewer than 4 messages from you. Try
  a longer chat.
- **"I found no chat with that name."** Give the chat's exact title, or paste
  the chat, or point to a chat export file.
- **"I can't open past chats here."** The app you are using has no past-chat
  tools (Claude Code, for example). Paste the chat, point to an export file,
  or run the assessment inside that chat.
- **A named chat isn't found in the Claude app.** Claude's past-chat tools
  rely on chat search, which is part of the Claude app on paid plans: turn on
  Settings > Memory > "Search and reference chats".
- **No card.** The card appears only in claude.ai and Cowork, and only when
  Claude can create an artifact in that chat. The text result is complete
  without it.
- **Claude Code says it can't add the marketplace because "its source
  doesn't match"**. The marketplace is already registered, for example by
  the desktop app's Code tab. Update it instead:
  `claude plugin marketplace update modo-plugins`, then
  `claude plugin install modo-ai-skills@modo-plugins`.

## License

MIT. See [LICENSE](LICENSE). Made by [Modo](https://github.com/modo-learning).
