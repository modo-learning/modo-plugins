# Modo Task Finder

Modo Task Finder looks through your recent Claude chats, finds the tasks you
keep coming back to, estimates the time they take, and suggests one practical
fix for each: a reusable skill, a scheduled task, a connector to add first,
or a tweak to something you already have. If you say yes to a fix, it builds
it with you.

It's made for people who use Claude every day for real work (emails,
reports, prep, updates) and keep re-pasting the same context and
re-explaining the same rules.

## What you get

Run it and you get a short list, most frequent first, of up to six repeated
tasks. Each one shows:

- roughly how many chats it came up in
- what you keep re-explaining or re-pasting
- one fix, and what it would do
- a rough time estimate
- one or two example chats, so you can check it yourself

It ends by offering to build the top fix. Nothing is built unless you say
yes. After a fix, it offers once to run the check weekly.

### Example

This example is made up; the names and tasks are invented.

> I looked at 29 chats from Sep 1 to Sep 30. Four tasks repeat, most
> frequent first.
>
> 1. **Weekly client status report** (6 chats). Each Friday you paste the
>    week's project notes and re-explain the format: done, in progress,
>    risks, one page, no ticket numbers. Fix: a **skill** that holds the
>    format, so you only paste the notes. About 15 min each, about 1.5 hours
>    this month. Examples: "Acme weekly status report" (Sep 4, Sep 25).
> 2. **Candidate outreach messages** (5 chats). Same rules every time:
>    under 90 words, salary band up front, one detail from their profile.
>    Fix: a **skill**. About 25 minutes this month.
> 3. **Expense reconciliation** (4 chats). You export transactions from
>    your accounting tool by hand each week. Fix: **needs a connector
>    first**. About 1.3 hours this month.
> 4. **Monthly investor update** (3 chats). **Already covered** by your
>    investor-update skill. One tweak: apply late edits to the existing
>    drafts instead of redoing them.
>
> Left out: a one-off pricing model session, and a task that only came up
> twice. 1 and 2 fit as skills, 3 needs a connector. Want me to build the
> status report skill?

## Install

**Claude Code**

```
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-task-finder@modo-plugins
```

**Claude (web, desktop, Cowork)**

Open Customize, then Plugins, choose Add marketplace, and paste
`https://github.com/modo-learning/modo-plugins`. Then install Modo Task
Finder from the list.

## Use

In Claude chat or Cowork, ask in plain words, for example:

- "What tasks do I keep repeating?"
- "Where is my time going in my chats? Look at the last 3 months."

In Claude Code, run `/modo-task-finder:my-tasks`, optionally with a window:
`/modo-task-finder:my-tasks 3 months`. Claude Code can't search your Claude
chats, so there it works from a chat export file or a description of your
week. For your chat history, run it in the Claude app.

The default window is the last 30 days. You can give another one, such as
"3 months" or "since Sep 1".

## Requirements

- A paid Claude plan (Pro, Max, Team or Enterprise) for chat search.
- Chat search turned on: Settings > Memory > "Search and reference chats".
  Chat search is part of the Claude app (chat and Cowork), not Claude Code.

Without chat search, it can still work from a chat export file you point it
to, or from a description of your typical week.

## What it reads, and your privacy

- **What it reads:** your past Claude chats in the window you choose, using
  Claude's own chat search in your account. It lists chats, runs several
  searches, and opens up to 15 chats when a title isn't clear enough. If you
  point it to a chat export file, it reads that file instead. If you
  describe your week, it uses only your description.
- **What it doesn't do:** it makes no calls to any outside service, sends
  your chats nowhere, and doesn't save notes, logs or files. Everything
  happens inside your conversation with Claude.
- **What it can't see:** incognito chats, and chats that Claude's chat
  search doesn't return. In Cowork, chat search doesn't include older Cowork
  tasks.
- **When it writes something:** only when you say yes to a fix. It then
  proposes that skill or scheduled task, and you decide whether to save or
  create it. In the Claude app a skill appears as a Save skill card you can
  save or dismiss.
- **What it doesn't look for:** it reads only the export file you name, and
  never searches your computer for other history such as coding-tool logs.

The plugin is a set of instructions for Claude. It contains no code, no
connectors and no background processes. You can read all of it in
`skills/my-tasks/SKILL.md`.

## Troubleshooting

- **"I can't see your past chats."** Turn on Settings > Memory > "Search and
  reference chats". On Team and Enterprise plans, memory is off for each
  member until it's turned on, and an owner may need to make it available
  first.
- **Fewer chats than expected.** Chat search only returns chats from your
  account that it can see. Chats inside a project are searched within that
  project; run it there too.
- **A task is missing.** You need to have asked for it at least 3 times in
  the window (in separate chats, or as fresh requests inside one long chat),
  or spent 2 long sessions on it. Try a longer window, such as "3 months".
- **Claude Code says it can't add the marketplace because "its source
  doesn't match"**. The marketplace is already registered, for example by
  the desktop app's Code tab. Update it instead:
  `claude plugin marketplace update modo-plugins`, then
  `claude plugin update modo-task-finder@modo-plugins`.
- **The fix type looks wrong.** Say so ("make that one a scheduled task")
  and it will build that instead.

## License

MIT. Made by [Modo](https://github.com/modo-learning).
