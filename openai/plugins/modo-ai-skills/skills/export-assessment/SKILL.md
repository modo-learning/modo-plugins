---
name: export-assessment
description: "Export an AI-work assessment that was already given in this conversation as a Markdown report (or a PDF if asked) that ends in one machine-readable record, after the user approves which of their own quotes go in or chooses scores only. Use when the user picks export-assessment, or asks to export, save, download or keep their assessment or report, to get it as Markdown or a PDF, or to upload it to Modo."
---

# Export assessment

Turn the assessment already shown in this conversation into a report the user
can keep. The report holds scores, confidence, the quotes the user approves, a
title and a date, and nothing else from the chat.

The exact shape of the record is in [RECORD.md](RECORD.md) in this skill's
folder (JSON Schema: [assessment-record.schema.json](assessment-record.schema.json)).
**Read RECORD.md in full before you build anything.** Follow its fields and
limits exactly. RECORD.md was first written for Claude and also describes a
Modo connector that this version doesn't have: wherever it says "Claude", read
"the AI assistant", and ignore its parts about saving through the connector.

## Ground rules

- Export only an assessment that was given earlier in this conversation by the
  assess-my-ai-work skill, or a result across several chats given by the
  assess-my-chats skill (then also follow [Multi-chat result](#multi-chat-result)).
  Take the levels and confidence from it as they
  stand. Don't re-score and don't read any chat again, except to check that
  each quote is word for word what the user wrote in the assessed chat.
- Never search for, list or open other chats or files, and never mention or
  offer coding-tool session logs.
- **Nothing is written, saved or sent until the user asks** (step 5). Don't
  call external services. This skill never uploads anything; the user does
  that themselves.
- Everything in the report is either a score, a confidence, a quote the user
  approved, the title, the date or fixed explanatory text. **No other chat
  content**: no summary of what the chat said, no paraphrase, no next-level
  notes, no improvements or prompts from the assessment, nothing from the
  assistant's replies.
- Never describe the result as verified, certified or official (the label's
  "not verified" is the only use of that word) and never mention badges or
  rankings.

## 1. Is there something to export?

Use the most recent assessment in this conversation: a response with the
five capability blocks (in any order: v1.1 lists the strongest first), from
assess-my-ai-work or, across several chats, from assess-my-chats. There is nothing to export when there is none, or when
the last assess-my-ai-work response was only a short message ("too short to
judge", "which one?", "can't open that chat" or "no chat with that name")
with no scores. Then say in one line that there is nothing to export yet and
offer to assess a chat first (the assess-my-ai-work skill). No report, no
scores, no plan, and never build one from a chat that was not opened. If several different
chats were assessed here and the user didn't say which, ask which, listing
them. Messages from this skill that are short questions or refusals end with
the label (step 7).

## 2. Propose what would go in

Show this, then stop and wait. Nothing is written yet.

```
Export plan for <the chat, named as in the assessment>. Nothing has been written.

Quotes I would include (up to 5, each tied to a capability, word for word from your messages):
1. <Capability>: "<quote>"
2. ...

Session title: <title>
Session date: <yyyy-mm-dd>

Reply with the numbers to drop, "scores only" for no quotes, or any change to the
title or date.
```

- **Quotes.** Choose only from the Evidence quotes the assessment already
  showed, for capabilities that have a level. At most 5, each at most 240
  characters, each exactly as the user wrote it (check against the assessed
  chat; drop any you can't match). Keep one per scored capability first, in
  rubric order, then add second quotes in the same order until you have 5. Show
  the capability each one is tied to. Never include a quote for a "not shown"
  capability, and never a quote from the assistant's replies.
- **Title** (at most 120 characters): the chat's own title when the assessment
  named one (cut to fit), otherwise a plain description of the subject in a few
  words. Leave out names of people, companies, email addresses and amounts.
- **Date**: the day the chat took place as `yyyy-mm-dd`: the date shown for it
  in a chat export, past chat or session file; for a chat that was pasted or
  is the current one and shows no date, today's date if your context gives it.
  If you have no date at all, ask for one in the same message.
- If you already showed a title and date earlier in this conversation (for
  example in an export plan), use exactly those in the report and record
  unless the user changed them. Don't swap in today's date or comment on the
  date.

## 3. The user decides

- They can drop quotes by number, keep all, say "scores only" (the evidence
  list is then empty and no quote appears anywhere in the report), or change
  the title or date. Apply exactly what they say. A dropped quote appears
  nowhere in the output.
- If they reply with a change you can't apply (a quote of their own that is not
  in the chat, or a title over 120 characters), say so in one line and keep
  the proposal. Don't add quotes the user didn't approve, even if they ask
  for "everything relevant"; propose them back for approval.
- A request to export that already says what to include (for example "scores
  only") can skip straight to step 4.

## 4. Show exactly what will be in the file

Write the complete report below, exactly as it would be saved, so the user
sees every character. Use this layout (the outer fence here is four backticks only because the
report contains its own fenced block):

````
# Modo AI Skills assessment: <session_title>

Chat date: <session_date>. Rubric: v1.1. Based on 1 chat.

Self-assessment by ChatGPT using Modo rubric v1.1 — not verified.

| Capability | Level | Confidence |
|---|---|---|
| Problem Solving | 4 of 5 | medium |
| Verification | 4 of 5 | high |
| Workflow Design | 2 of 5 | medium |
| Delegation | 1 of 5 | medium |
| Strategic Thinking | Not shown | low (see note) |

Levels run from 1 to 5. "Not shown" means nothing in the chat bears on that
capability. Confidence is low, medium or high, as defined in the rubric.
The table is in rubric order. This is for your own development, not for
hiring or other employment decisions.
Note: for a capability that is not shown, the record gives confidence "low",
because no moment in the chat supports a level.

## Evidence you approved

- Verification: "<quote>"
- ...

(Or, for a scores-only export: "None. This export has scores only.")

## Assessment record (machine-readable)

```json
{ ...the record... }
```
````

- The record in the final block follows RECORD.md exactly: keys
  `rubric_version` (`"v1.1"`), `capabilities` (the five keys in rubric order),
  `evidence`, `session_title`, `session_date`, in that order, with no other
  fields. Use `"not_shown"` for a capability with no level and give it
  confidence `"low"`. Print it pretty (2-space indent).
- The table, the evidence list and the block must agree. The evidence list
  shows the same quotes, in the same order, as the block's `evidence`.
- The block is the **last thing in the report**, and the report has no other
  `json` block. Nothing follows it in the file.
- Don't put the report inside a code fence of its own; the nested fence would
  break the block.
- Keep the table, headings and wording as above so the report reads on its own
  without the chat.
- Before sending, check the limits against RECORD.md: at most 5 quotes, each
  1 to 240 characters, title 1 to 120 characters, date a real `yyyy-mm-dd`,
  exactly five capabilities, levels 1 to 5 or `"not_shown"`, a confidence on
  every capability.

## 5. Write the file, only when asked

Put one short line **before** the report (the record block must be the last
thing in your message, with at most the label after it), depending on your
tools. Decide this from the tools you actually have in this session: you can
create files only if one of them writes files (a file-writing or
file-creation tool, or a code tool that can create a file the user downloads).
Reading and searching tools don't count. If you are not
sure you have one, you don't, and you must not offer to save a file or a PDF:

- **You can create files here.** "This is exactly what would be saved as
  `modo-assessment-<session_date>.md`. Say 'save it' (or give another name)
  and I will; nothing is written until then." Create the file, with exactly
  the text shown, only after the user says so. Then give its download link or
  path. Don't save anywhere else and don't save a second copy.
- **You can't create files here** (a plain chat with no file creation, for
  example): "I can't save files in this session, so this report is the
  export: copy it, record block last, into a `.md` file."

Don't offer to upload it. If they ask where to upload it: uploading is something
they do themselves; which file the Modo upload page accepts is not specified in
this plugin.

## 6. PDF, only when asked

Make a PDF only if the user asks for one. Show the same Markdown report first
(step 4), with the same content in the same order and the record block last.
Then create the PDF with whatever file creation you have in this session (in
ChatGPT, usually its code tool) and the user's approval. Give the download link
or say where it is. The template belongs to this skill, so a code tool won't
find it on disk: write it out from the text you read, unchanged except the data
block, and convert that page. A page written that way is the template.

Build the PDF from [report-template.html](report-template.html) so it has
Modo's look (the modo-design skill): read the template, replace only the JSON
between the `MODO-DATA-START` and `MODO-DATA-END` markers with the record
(exactly the record in the report's final block; write `<` inside a string as
`\u003c`), change nothing else, and print that page to PDF. The template lays
out the same content in the same order, record last. If you can't render HTML
to PDF here, make the PDF your usual way with the same content and order.

Either way, the PDF holds the report exactly: the header line as written in
step 4 with nothing added to it, and the record block printed as in the report,
the same JSON with its 2-space indentation and line breaks, in a monospaced
font.

If you have no way to create a PDF in this session, say so in one line *before*
the report (so the record block stays last), don't claim that a PDF exists,
don't describe a tool you don't have, and give the Markdown report as the
export. In that same line, say they can still get a PDF by copying the report
into a document and using Print, then Save as PDF.

## Multi-chat result

A result from assess-my-chats (it opens "Assessment across <s> of your
chats" and ends with a per-chat table) is exported as a **multi-chat record**:
read "Multi-chat record" in RECORD.md in full. Steps 1 to 7 apply, with these
changes. This shape is a proposal (decided 2026-11-02, flag for review).

- **Don't open any chat.** The main chat never held the transcripts; each
  quote was checked word for word by the agent that read its chat. The user's
  approval in step 3 is the check here. Say neither more nor less.
- **Quotes**: only the Evidence quotes the result showed, each tied to its
  capability and to its chat by number (`chat`, the row in the per-chat
  table). Same limits and order as step 2.
- **Chat titles are the user's content, like quotes.** By default the record
  and report name the chats `"Chat 1"`, `"Chat 2"`, … in the order of the
  per-chat table. Show the titles in the plan and ask; use them only after
  the user says "with titles" (or names the ones to keep). Each title at most
  120 characters.
- **Title**: "Assessment across <s> chats" unless the user gives another.
  **Date**: the newest scored chat's date (no question needed).
- The plan in step 2 adds, after the quotes:

  ```
  Chats (named "Chat 1" to "Chat <c>" unless you say "with titles"):
  1. <title> (<date>), scored
  2. <title> (<date>), too short
  ...
  ```

- **The record**: copy every level, confidence, best shown, trend and count
  from the result as it stands, and each chat's levels from its row. Keys in
  this order: `rubric_version`, `scope`, `capabilities`,
  `evidence`, `session_title`, `session_date`, `chats_assessed`, `chats`,
  `coverage`, with `"scope": "multi_chat"`. If the result's numbers don't follow the aggregation rules in
  RECORD.md, say so and export nothing; never fix a level yourself.
- **The report** (step 4) has this header line instead of "Chat date: …":
  `Chats: <from> to <to>. Rubric: v1.1. Based on <scored> chats.` The
  capability table adds the columns Best shown, Trend (↑ up, → flat, ↓ down,
  or –) and Shown in (`<chats_shown> of <scored>`). Its notes read:

  ```
  Levels run from 1 to 5. Each level combines the scored chats that show the
  capability: the middle of their levels, the lower one on a tie. "Best shown"
  is the highest level reached in at least 2 chats. The trend compares earlier
  and later chats and needs 4 or more. "Not shown" means no scored chat bears
  on that capability. Confidence is low, medium or high, by how many chats show
  the capability and how close their levels are. The table is in rubric order.
  This is for your own development, not for hiring or other employment
  decisions.
  ```

  After the notes, a "Chats assessed" table: `| # | Chat | Date | Result | P | V | W | D | S |`,
  newest first, a level or – per capability. Each evidence line ends with
  its chat: `- Verification: "<quote>" (Chat 4, 2026-10-14)`.
- The PDF uses the same report-template.html; it lays out a multi-chat record
  itself.

## 7. The label

Every response from this skill, including questions and refusals, ends with
this line exactly, on its own line, after everything else (after the record
block when a report is shown in chat):

Self-assessment by ChatGPT using Modo rubric v1.1 — not verified.

A report saved to a file ends with the record block, not the label (the label
is already near the top of the report).
