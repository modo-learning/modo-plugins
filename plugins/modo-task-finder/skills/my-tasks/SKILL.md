---
name: my-tasks
description: Find the tasks the user keeps repeating across their past Claude chats, estimate the time they cost, and suggest one fix for each (a skill, a scheduled task, a connector to add, or "already covered"). Use when the user runs /my-tasks, or asks what they keep repeating, where their time goes, what they could automate, or which of their chats are routine.
argument-hint: "[window, e.g. 3 months or since Sep 1]"
---

# My tasks

Find the work this user keeps redoing across their past chats, and turn each
repeated task into one concrete fix. The value is in being specific and
honest: real counts, real examples, the user's own tools and wording. A
short accurate list beats a long plausible one.

## Ground rules

- Only report what the chats show. Never invent chats, counts, dates or
  tools. If the evidence is thin, say so and list fewer items.
- Everything stays in this conversation. Don't call external services, don't
  write files, don't save notes or logs. The only exception is a fix the user
  explicitly says yes to.
- Skip incognito chats and anything the tools don't return. Don't try to
  reconstruct chats you can't see.
- Use the user's own words for tasks, people and tools, but don't quote
  private message content at length. A short title or date is enough as
  evidence.

## 1. Work out the window

- Default: the last 30 days, ending today.
- If the user gives one (`3 months`, `since Sep 1`, `2026-09-01 to
  2026-09-30`), use it. Turn it into a start date and an end date before
  doing anything else, and say it in the first line of the answer.

## 2. Find the chat history

Use the first source that works. If the user has already described their
work in the request and says chat search isn't available, go straight to 4.

1. **Claude's past-chat tools.** Look for tools that list recent chats,
   search past chats, or open a past chat. In claude.ai they have been seen
   as `recent_chats`, `conversation_search` and `read_conversation`, but use
   whatever equivalent tools you have.
2. **A chat export the user points to**, such as the `conversations.json`
   from Claude's data export, or any file of past chats. Read it with your
   file tools. Don't assume an exact format: find each chat's title, date and
   the user's messages, whatever the field names are.
3. **Neither available.** Don't guess and don't produce a list. Tell the user
   plainly that you can't see their past chats, then give them three ways
   forward:
   - Turn on chat search in Claude: Settings > Memory > "Search and
     reference chats". It needs a paid plan. On Team and Enterprise plans,
     memory is off for each member until it's turned on, and an owner may
     need to make it available first. Then run this again.
   - Point you to a chat export file.
   - Describe a typical week or month of their work right here, and you'll
     find the repeated tasks in that instead.
   Then wait for their answer.
4. **The user describes their work** (now, or up front). Run steps 4 to 8 on
   their description instead of on chats. Treat each thing they say happens
   regularly ("every Monday", "most days", "before each call") as a
   candidate. Use their stated frequency in place of a chat count, for
   example "(every Monday)" or "(about 4 a week)", and skip chat examples as
   evidence. Say in the opening line that the list is based on what they
   described, not on their chat history. Something they did once is a
   one-off, however big.

## 3. Gather every chat in the window

Build one inventory of chats: id, title, date, and a one-line note of what
the user was doing.

**With past-chat tools:**
- List chats with the recent-chats tool, starting from the window's start
  date. If a page comes back full, page back further (for example with a
  `before` date set to the oldest chat seen) until you pass the start date or
  stop getting new chats.
- Then run 8 to 12 searches for routine work, because search results are
  capped and a listing can miss things. Start with: `draft`, `reply`,
  `email`, `update`, `report`, `summary`, `prep`, `rewrite`, `follow up`,
  `again`, `same as last time`. Add a few queries built from titles that
  already look repeated.
- Search results are not limited to your window. Drop every chat dated
  outside it.
- The same chat can come back many times, sometimes with different dates.
  Keep one entry per chat id and use its most recent date.
- When a title is too vague to tell what the user was doing, open the chat.
  Open at most 15 chats in total, choosing the vaguest titles first.

**With an export:** read the file, keep chats whose date falls inside the
window, and note what the user was doing from the title and their first
messages.

Count what you gathered: the number of chats in the window. You'll report it.

## 4. Group chats by task

Group by the **job the user was doing**, not by topic words. "Draft the
weekly status report for the client" is one job even if the project changes;
"write a cover letter" and "write a toast" are different jobs even though
both are writing.

A group qualifies as a **repeated task** when either:
- it appears in **3 or more separate chats** in the window, or
- it took **2 or more long sessions** (roughly 10+ back-and-forth turns each)
  on the same recurring job.

Drop:
- groups of 1 or 2 short chats,
- a single long session on a one-off project, however big,
- anything dated outside the window, even if it repeated before.

Look for the signal that makes a task worth fixing: the user re-pastes the
same context, re-explains the same rules or format, or does it on a
schedule (every Friday, after every call, each month).

## 5. Rank and cap

Sort by number of chats, most first. Keep the **top 6**. If fewer qualify,
show fewer. Never pad the list.

## 6. Estimate the time cost

For each task, give a rough time estimate: minutes per occurrence times the
number of occurrences in the window. Base it on what the chats show (how much
was pasted and re-explained, how many rounds of edits). Label it as an
estimate, for example "about 15 min each, about 1.5 hours this month".

## 7. Pick exactly one fix per task

Choose the single best fix:

- **Skill**: the user keeps re-explaining the same rules, format, voice or
  reference material. A skill captures it once, so next time it's a
  one-line ask.
- **Scheduled task**: the work is triggered by time or a regular event
  (every Friday, the evening before meetings, each month), so it can run
  without being asked.
- **Needs a connector first**: the user keeps copying data in by hand from a
  tool Claude isn't connected to. Name the tool. Automation comes after the
  connection.
- **Already covered**: the user already has a skill, plugin or scheduled task
  for this. Check the skills and plugins you can see in your context. If the
  chats show friction anyway (late edits, redoing output), suggest one tweak.
  You can't see scheduled tasks, so if one seems likely, add "if you already
  have a scheduled task for this, ignore this one".

Don't offer alternatives ("a skill or maybe a scheduled task"). Commit to one.

## 8. Write the answer

Plain chat text, no tables, no headings. Keep it short enough to read in a
minute.

1. One opening line: the window, roughly how many chats you looked at, and
   that the list is most frequent first.
2. One short paragraph per task, numbered:
   - **Bold task name**, then the count in brackets, e.g. "(about 6 chats)"
     or "(4 long sessions)".
   - What the user keeps doing or re-explaining, in their own terms.
   - The fix, naming its type in the words above, and what it would do.
   - The time estimate.
   - Evidence: one or two example chat titles or dates.
3. If you dropped something the user might expect to see (a big one-off
   project, a pattern from before the window), mention it in one line.
4. Close with one line grouping the fixes ("1 and 2 fit as skills, 3 as a
   scheduled task...") and a single question offering to build the top one.

Don't build anything until the user says yes.
