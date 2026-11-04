---
name: save-to-passport
description: "Save an AI-work assessment already given in this conversation to the user's Modo passport through the Modo connector, after showing the exact record and getting a clear yes; or show the user's Modo passport. Use when the user runs /save-to-passport, or asks to save, send or add their assessment to Modo or their Modo passport, or to see their Modo passport, latest scores or assessment history."
---

# Save to my Modo passport

Send the assessment already shown in this conversation to the user's Modo
passport, but only the exact record they saw and only after they say yes. Or
show them their passport.

The record is defined in [RECORD.md](RECORD.md) in this skill's folder (JSON
Schema: [assessment-record.schema.json](assessment-record.schema.json)).
**Read RECORD.md in full before you build a record.** It is the whole input of
the save tool: nothing else is ever sent.

## Ground rules

- **Is the Modo connector here?** Look at the tools you have in this session.
  The Modo connector is present only if you have a tool named
  `save_assessment`, or one whose name ends in `__save_assessment` (for example
  `mcp__modo__save_assessment`); a tool listed only by name (deferred) counts.
  Its passport tool is `get_passport`, or the name ending in `__get_passport`
  on the same connector. Call each tool by the exact name your session lists,
  loading a deferred tool first the way your session loads deferred tools.
- **No connector**: say in one line that the Modo connector isn't connected in
  this session, so you can't save to or show the Modo passport here; offer the
  export instead (the user can ask to export the assessment as a report).
  Nothing else: no record, no instructions for installing anything. End with
  the label (step 7).
- Save only an assessment given earlier in this conversation by the
  assess-my-ai-work skill, or a result across several chats given by the
  assess-my-chats skill (then also follow [Multi-chat result](#multi-chat-result)).
  Take the levels and confidence from it as they
  stand. Don't re-score and don't read any chat again, except to check that
  each quote is word for word what the user wrote in the assessed chat.
- Never search for, list or open other chats or files.
- **Nothing is sent until the user has seen the exact record and said yes to
  it** (step 4). Never send a transcript, a summary, Claude's replies, the
  next-level notes, the improvements or any field that is not in RECORD.md.
- Never describe the result as verified, certified or official (the label's
  "not verified" is the only use of that word) and never mention badges or
  rankings.

## 1. Is there something to save?

Use the most recent assessment in this conversation: a response with the five
capability blocks. If there is none, or the last assessment response was only
a short message ("too short to judge", "which one?", "can't open that chat",
"no chat with that name") with no scores, say in one line that there is
nothing to save yet and offer to assess a chat first. If several chats were
assessed here and the user didn't say which, ask which, listing them.

If the user only wants to see the passport, go to step 6.

## 2. Build the record

Follow RECORD.md (these are the same rules the export uses):

- **Quotes**: only from the Evidence quotes the assessment already showed, for
  capabilities that have a level. At most 5, each at most 240 characters, each
  word for word as the user wrote it (drop any you can't match). One per scored
  capability first, in rubric order, then second quotes in the same order
  until you have 5. Never a quote for a "not shown" capability, never one from
  Claude's replies.
- **Title** (at most 120 characters): the chat's own title when the assessment
  named one (cut to fit), otherwise a plain description of the subject in a
  few words, without names of people, companies, email addresses or amounts.
- **Date**: the day the chat took place, `yyyy-mm-dd`: the date shown for it
  in a chat export, past chat or session file; for a chat that was pasted or
  is the current one and shows no date, today's date if your context gives it.
  If you have no date at all, ask for one.
- If an export plan or report was already approved in this conversation, start
  from its quotes, title and date.
- If the user already said what to include ("scores only", "without quote 3"),
  apply it now. It still has to be shown and confirmed (steps 3 and 4).
- Fields, in this order and no others: `rubric_version` (`"v1.1"`),
  `capabilities` (the five keys in rubric order, each `level` and
  `confidence`; `"not_shown"` gets confidence `"low"`), `evidence`,
  `session_title`, `session_date`. Check every limit in RECORD.md before
  showing it.

## 3. Show exactly what will be sent, then stop

Show this and wait for the user's answer. Don't call the save tool in the same
response.

````
This is exactly what I would send to your Modo passport. Nothing has been sent yet.

Quotes (word for word from your messages):
1. <Capability>: "<quote>"
2. ...

```json
{ ...the record, pretty printed with 2-space indent... }
```

Say "send it" to save exactly this record. Or reply with quote numbers to drop,
"scores only" for no quotes, a change to the title or date, or "no" to send nothing.
````

For a record with no quotes, the quotes list reads "None (scores only)." The
list and the block must show the same quotes in the same order.

## 4. The user decides

- **A clear yes to this record** ("yes", "send it", "save it", "go ahead"):
  call the save tool once, with the record exactly as last shown as its
  arguments: the record's five fields are the top-level arguments, not wrapped
  in another object. Then step 5.
- **A change** (drop quotes, scores only, a new title or date): apply exactly
  that, then show the whole updated record again (step 3) and wait for a yes.
  A change is never a yes, even when it says "and save it": the user must see
  the record that will really be sent. A dropped quote appears nowhere.
- A change you can't apply (a quote that isn't in the chat, a title over 120
  characters): say so in one line and keep the record as it was shown.
- **No, not now, or anything that isn't a clear yes**: send nothing. Accept a
  no in one line, without the record and without arguing; ask when the answer
  is unclear.
- Your tool-approval prompt, if Claude shows one, is a second check, not a
  replacement for the user's yes.

## 5. After the call

- **Saved**: say in one or two lines that it is saved to their Modo passport,
  with the title and date the tool returned. Then ask whether they want to see
  their passport. Don't show it unless they say yes.
- **The tool returns an error**: say plainly that nothing was saved and what
  the server said, in plain words (quote the server's message). The next call
  waits for the user to ask, and it sends the record exactly as last shown and
  confirmed: never another rubric version, a shortened quote or an edited
  level to get it accepted. Then, by the error:
  - **A rule the user can meet by a change** (dropping a quote, a shorter
    title): propose that change as a new record and go back to step 3.
  - **The server could not store it** ("could not be stored", "try again
    later"): tell the user they can ask you to try again later, and offer the
    export to keep the assessment now.
  - **Anything else** (for example the server doesn't accept this rubric
    version): say so and offer the export instead.
- **Saved with no clear result** (no error, no confirmation): say you can't
  tell whether it was saved, and don't call it again unless the user asks.

## 6. Show the passport

Only when the user asks or says yes to the offer. Call the passport tool with
no arguments, then show what it returned, in plain text:

```
Your Modo passport.

Latest level per capability (rubric v1.1):
Problem Solving: Level 4 of 5 (confidence: medium), from 2026-10-20
...
Strategic Thinking: Not shown yet

History (newest first):
- 2026-10-20, "Q3 pricing analysis for the board" (rubric v1.1): Problem Solving 4, Verification 4, Workflow Design 2, Delegation 1, Strategic Thinking not shown
```

Use the five capabilities in rubric order; a capability with no latest level
is "Not shown yet". Show only what the tool returned: don't add levels, quotes
or comparisons. An empty history means nothing has been saved yet: say so. On
an error, say the passport couldn't be read and that they can try again later.

## Multi-chat result

A result from assess-my-chats is saved as a **multi-chat record**
(`"scope": "multi_chat"`): read "Multi-chat record" in RECORD.md in full. This
shape is a proposal (decided 2026-11-02, flag for review).

- **First check the server takes it.** Look at the save tool's input fields.
  If the tool has no `scope` field, the Modo connector can't store a result
  across several chats yet: say so in one line, send nothing, and offer the
  export (/export-assessment) instead. Don't reshape the result into a
  single-chat record to get it accepted.
- Build the record as export-assessment's "Multi-chat result" says (if an
  export of it was approved here, start from that): quotes only from the
  result, each with its chat number; chats named `"Chat 1"`, `"Chat 2"`, …
  unless the user says "with titles"; title "Assessment across <s> chats";
  date the newest scored chat's date; every number copied as it stands, with
  `best_shown` worked out as that section says.
- Don't open any chat: the agents checked the quotes; the user's yes in step
  4 is the check here.
- Step 3 shows the chat list too, as the record names it, then the record.
  Steps 4 to 7 are unchanged.

## 7. The label

Every response from this skill, including questions, refusals and the
passport, ends with this line exactly, on its own line, after everything else:

Self-assessment by Claude using Modo rubric v1.1 — not verified.
