# Modo AI Skills

Modo AI Skills tells you how well you work with AI, from one Claude chat you
choose, against Modo's public rubric. For each of five capabilities (Problem
Solving, Verification, Workflow Design, Delegation, Strategic Thinking) you
get a level from 1 to 5, or "not shown", a confidence label, a quote from your
own messages as evidence, and what the next level looks like. Then it gives
you two concrete improvements for your weakest areas, each with a prompt to
try next time.

It's made for people who use Claude every day for real work and want honest
feedback on how they frame problems, check Claude's work, build repeatable
workflows, hand work over and decide where AI is worth using, with something
concrete to keep.

## What you get

- **A level for each capability**, written as "Level N of 5", tied to the
  level descriptions in the [rubric](skills/assess-my-ai-work/rubric-v1.md).
  A capability the chat did not show is "Not shown in this chat", never a
  made-up score and never level 1.
- **A confidence label** (low, medium or high) on each level, set by how much
  the chat showed, as defined in the rubric.
- **Evidence**: one or two exact quotes from your own messages behind each
  level. Claude's replies are context only; they are never quoted as
  evidence.
- **Next level**: one line on what the next level up would look like for you.
- **Improvements**: for the two weakest capabilities that were shown, a
  technique taken from the rubric and a "try this next time" prompt you can
  paste as it stands. It then offers (only offers) to turn them into one
  reusable skill.
- **A card** in claude.ai and Cowork (see [The card](#the-card)).
- **An export** when you ask for one (see [Export a report](#export-a-report)).

Every result ends with this label:

> Self-assessment by Claude using Modo rubric v1 — not verified.

It is Claude's reading of one chat against a public rubric. It is not a test,
a certificate or a comparison with other people.

## Install

**Claude Code**

```
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-ai-skills@modo-plugins
```

**Claude (web, desktop, Cowork)**

Open Customize, then Plugins, choose Add marketplace, and paste
`https://github.com/modo-learning/modo-plugins`. Then install Modo AI Skills
from the list.

If you already have Modo Task Finder, the marketplace is already added; just
install Modo AI Skills from it.

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
also shown as an **AI capability card** beside the chat: which chat was
assessed, five rings (one per capability, with its level and, for a shown capability,
its confidence), the
one or two strongest quotes from the assessment, and the label. The rubric's
level band sets how full each ring is; a capability that was not shown has
an empty ring marked "Not shown", never a zero. The card holds nothing that
isn't in the text result, is not saved anywhere else, and makes no network
calls.

In Claude Code the result stays plain text and there is no card. Samples:
[dark](docs/passport-card-sample.png) and
[light](docs/passport-card-sample-light.png).

## Improvements and the skill offer

After the five levels, the assessment picks the two weakest capabilities that
were shown (or the only one, if just one was shown; never a "not shown" one) and gives each a technique from the
rubric and a prompt to try next time. It then asks whether you want them
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
   session.

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
  ever sent anywhere.
- **What it writes:** nothing, unless you ask. The only exceptions are the
  card in claude.ai and Cowork (shown beside the chat), a skill you choose to
  save, and an export file you ask for.
- **Saving to Modo:** not available yet. A Modo connector that saves an
  assessment to your Modo passport is planned for a later release. When it
  comes, Claude will show you the exact record it would send (the same fields
  as the export: levels, confidence, the quotes it proposes, title and date),
  let you drop quotes or choose scores only, and send it only after you
  confirm. It will never send a transcript.

The plugin is a set of instructions for Claude, plus the card template (an
HTML page whose small script draws the rings and makes no network calls). It
contains no connectors and no background processes. You can read all of it
in the `skills/` folder.

## The rubric

The rubric is public and versioned:
[skills/assess-my-ai-work/rubric-v1.md](skills/assess-my-ai-work/rubric-v1.md).
It is how scores are calculated, including the rules for "not shown",
confidence and the card's rings. The help-me-improve skill keeps an identical
copy so each skill folder is self-contained; a check in the plugin's source
repository keeps the two copies identical.

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
