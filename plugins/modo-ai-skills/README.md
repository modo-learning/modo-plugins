# Modo AI Skills

Modo AI Skills tells you how well you work with AI, from one Claude chat you
choose, against Modo's public rubric. For each of five capabilities (Problem
Solving, Verification, Workflow Design, Delegation, Strategic Thinking) you
get a level from 1 to 5, or "not shown", a confidence label, a quote from your
own messages as evidence, and what the next level looks like. Then it gives
you two concrete improvements for your weakest areas, each with a prompt to
try next time.

**Not for hiring or employment decisions.** Modo AI Skills is a
self-assessment for your own development. It is not intended for hiring,
promotion, performance reviews or any other employment decision about you or
anyone else.

This branch carries **rubric v1.1**: scoring prompt by prompt against
published behaviours, a fixed level rule, 3 to 5 scoring runs with their
agreement shown, honest coverage for thin chats, and a redesigned card. See
[What changed in v1.1](#what-changed-in-v11).

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

This version (rubric v1.1) lives on the branch `modo-ai-skills-v1.1` of this
repository. The earlier version (rubric v1) stays on `modo-ai-skills-phase0`,
so the two can be compared. Neither is on `main`, so install from a branch.

### claude.ai, the Claude desktop app and Cowork

The marketplace there reads only `main`, so upload the plugin as a zip:

1. Build the zip from a clone (the v0.1.0 test build on the releases page
   is rubric v1). Don't use GitHub's "Download ZIP" for the whole
   repository: it holds two plugins, and the upload takes one.

   ```
   git fetch origin modo-ai-skills-v1.1
   git archive --format=zip -o modo-ai-skills.zip origin/modo-ai-skills-v1.1:plugins/modo-ai-skills -- . ':!evals'
   ```

2. Open **Customize → Plugins → Add → Upload plugin** and choose the zip.
3. To assess a past chat by its title, turn on **Settings → Memory →
   "Search and reference chats"**.
4. Start a new chat, work on something real for at least 4 messages, then ask
   "how good am I at using AI in this chat?", and then "export it".

To update, remove the plugin in Customize → Plugins and upload the new zip.

### Claude Code

Add the marketplace at the branch:

```
claude plugin marketplace add modo-learning/modo-plugins#modo-ai-skills-v1.1
claude plugin install modo-ai-skills@modo-plugins
```

If you already added `modo-plugins` from `main` (for Task Finder), remove it
first. Removing it also uninstalls Task Finder, so install that again; the
branch has it too, unchanged:

```
claude plugin marketplace remove modo-plugins
claude plugin marketplace add modo-learning/modo-plugins#modo-ai-skills-v1.1
claude plugin install modo-ai-skills@modo-plugins
claude plugin install modo-task-finder@modo-plugins
```

To update: `claude plugin marketplace update modo-plugins`, then
`claude plugin update modo-ai-skills@modo-plugins`.

## How to ask

In Claude chat or Cowork, ask in plain words, for example:

- "How good am I at using AI?"
- "Assess this chat."
- 'Assess my chat called "Q3 budget review".'
- "How do I get better at verification?"
- "Export this assessment."

Or run the skills by name. In Claude Code, and from the `/` menu in the Claude
app:

| Command | What it does |
|---|---|
| `/modo-ai-skills:assess-my-ai-work` | Assess one chat |
| `/modo-ai-skills:help-me-improve` | Help with one capability, without an assessment |
| `/modo-ai-skills:export-assessment` | Export the assessment you were just given |

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
strongest capability, then shows one row per capability, strongest first:
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

## What it reads, what it sends, and your privacy

- **What it reads:** only the one chat you pick, in one of the ways above. For
  an export, it reads the assessment already in your conversation and, to
  check your quotes, the chat that was assessed. It does not read any other
  chat or file.
- **What it never does:** browse or search your chat history, list your
  chats, look for files or logs on your computer, or mention coding-tool
  session logs unless you point to one.
- **What it sends:** nothing. It calls no outside service. Everything happens
  inside your conversation with Claude. No transcript and no other chat is
  ever sent anywhere. Where Claude can start its own sub-tasks (subagents in
  Claude Code), the repeated scoring runs may each be a sub-task inside your
  session; each gets only the rubric and your messages from the chat you
  picked.
- **What it writes:** nothing, unless you ask. The only exceptions are the
  card in claude.ai and Cowork (shown beside the chat), a skill you choose to
  save, and an export file you ask for.
- **Saving to Modo:** not available yet. A Modo connector that saves an
  assessment to your Modo passport is planned for a later release. When it
  comes, Claude will show you the exact record it would send (the same fields
  as the export: levels, confidence, the quotes it proposes, title and date),
  let you drop quotes or choose scores only, and send it only after you
  confirm. It will never send a transcript.

The plugin is a set of instructions for Claude, plus two templates in Modo's
style, the card and the PDF report (HTML pages whose small scripts lay out the
result and make no network calls). It
contains no connectors and no background processes. You can read all of it
in the `skills/` folder.

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

| | Rubric v1 (`modo-ai-skills-phase0`) | Rubric v1.1 (this branch) |
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
