---
name: assess-my-ai-work
description: Assess how well the user works with AI in one chat (the current chat, a past chat they name, a chat they paste, a chat export file or a Claude Code session file they point to), scored against Modo's public rubric on five capabilities (Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking), with a level, a confidence label, quotes from the chat as evidence and what the next level looks like. Use when the user runs /assess-my-ai-work, or asks how good they are at using AI, to assess or score this chat, a named chat, pasted text or a file, or their AI skills, or how well they prompt, verify or delegate to Claude.
---

# Assess my AI work

Judge how the user worked with Claude in this chat, using Modo's public
rubric. The value is an honest score tied to their own words. A score without
a quote, or a level the chat doesn't support, is worse than "not shown".

The rubric is the file [rubric-v1.md](rubric-v1.md) in this skill's folder.
**Read it in full before scoring** and apply it exactly as written, including
its rules for choosing a level, "not shown" and confidence. Don't score from
memory or from your own idea of what good AI use looks like.

## Ground rules

- Assess **exactly one chat**, the one the user chose. Never search, list,
  skim or open any other chat, and never look around for files or logs. Do not
  mention or offer coding-tool session logs or transcripts (such as Claude
  Code's) unless the user themselves points to one. If the user asks for "all
  my chats", "my recent chats" or an overall picture, say in one line that you
  assess one chat at a time, and assess the current chat (step 0).
- Only the **user's own messages** are evidence. Claude's replies are context.
- Quote the user exactly, each quote under 240 characters. Never invent,
  paraphrase inside quotation marks or stitch quotes together.
- Everything stays in this conversation. Don't call external services, don't
  write files and don't save anything. The only exceptions:
  - the optional passport card (step 3), shown with the artifact tool and only
    in claude.ai or Cowork;
  - a reusable skill, only after the user says yes to the offer and only
    through the flow in step 6, where the user saves it themselves;
  - exporting a report, which is a separate skill (export-assessment) that
    runs only when the user asks for it. This skill never writes the report.
- Never describe the result as verified, certified or official (the label's
  "not verified" is the only use of that word), and never mention badges,
  rankings or comparisons with other people. "Verification" as the name of a
  capability is fine.

## 0. Find the chat

Use the first of these that matches what the user said.

- **No source named**: the current chat, meaning the messages exchanged here
  before the request to assess it.
- **Pasted text**: the chat the user pasted into their message. Their messages
  are the parts labelled as theirs ("You", "Me", "User", "Human" or similar).
  If you can't tell which parts are theirs, ask in one short question.
- **A file the user names** (a chat export such as `conversations.json`, or a
  Claude Code session file `.jsonl`): read only that file with your file
  tools, by the exact path given. If it doesn't exist or can't be read, say
  so and ask for the right path or for the chat pasted; don't search for it.
  - *Chat export*: each chat has a title, a date and a list of messages with
    the sender (`human` is the user). If the user named one chat, use the one
    whose title matches. If the file holds several chats and none was named,
    ask "which one?" and list the titles with dates. If it holds exactly one,
    use it.
  - *Claude Code session file*: one JSON object per line. The user's messages
    are the lines with `"type": "user"` whose message content is text the
    user typed. Lines of that type whose content is only `tool_result` blocks
    are tool output, not the user: never count or quote them. Tool calls and
    results are context for understanding what the user asked and checked.
- **A past chat the user names, without a file or pasted text**: find it
  only by its name. Never list recent chats, search by topic, or read any chat
  other than the one the user named.
  - If you have a tool that opens a chat by its name or exact title, use it
    with the user's name for the chat.
  - If the only past-chat tool you have is a search, run **one** search with
    the user's exact name for the chat as the query. Consider only results
    whose title is that name (letter case aside). Never read, show, list,
    quote or use the title, snippet or content of any other result, and don't
    search again with other words.
  - Exactly one chat has that title: open it and assess it.
  - More than one chat has that title: don't pick. Ask "which one?" in one
    short message that lists only those chats, each with its title and date.
  - No chat has that title: say you found no chat with that name, without
    naming or describing anything else the search returned, and offer two
    ways forward: paste the chat, or point to a chat export file.
  - No tool that can open or search past chats: say plainly that you can't
    open past chats here and offer three ways forward: paste the chat, point
    to a chat export file, or run this in the chat they want assessed.
  Never describe or score a chat you haven't opened.

Never guess which chat is meant. A question about which chat, or a statement
that you can't open one or found none with that name, is a short message of
its own: no scores, no rubric summary, nothing else besides the label
(step 7).

Then count and assess only that chat, with the same steps and output below.

## 1. Count the user's messages

Count the messages the user wrote in the chosen chat. For the current chat,
that means before the request to assess it. Don't count that request, pasted
tool output, tool results, or anything Claude wrote.

**Fewer than 4: stop here.** Don't score, don't hint at a level, don't give a
verdict. Say plainly which chat or file it was, that it is too short to judge (give the count and
the minimum of 4 messages from the user), that a short chat would give
misleading scores, and offer to assess a longer chat once they have one. End
with the label (see step 7).

## 2. Score each capability

For each of the five capabilities in the rubric, in this order: Problem
Solving, Verification, Workflow Design, Delegation, Strategic Thinking.

1. Find the user's messages that bear on it.
2. Pick the level (1 to 5) per the rubric, or **not shown** if nothing in
   their messages bears on it. Don't fill a gap with a middle score, and
   don't give level 1 for a lack of evidence: level 1 needs a quote that
   shows the low-level behaviour itself. Never use a quote as evidence for a
   capability it doesn't bear on.
3. Set confidence (low, medium, high) using the rubric's definitions.
4. Choose one or two exact quotes from the user's messages that justify that
   level.
5. Write one line on what the next level up would look like for this user, in
   the rubric's terms and, where you can, about this chat. For level 5, say
   what keeping it up looks like. For not shown, say what in a chat would show
   it.

## 3. The passport card (only where an artifact tool exists)

Do this after scoring and before writing the text answer (step 4). The text
answer is always written in full and is the result. A visual
card of the same result is an extra, shown only when **both** are true:

- you have a tool that creates an artifact (a page shown beside the chat), and
- you are in claude.ai or Cowork, not Claude Code (a terminal or IDE session,
  where the result stays text even if a publishing tool exists, because it
  would publish the result outside the chat).

If either is false, or the result is one of the short messages (too short,
"which one?", "can't open it", no chat with that name), or you can't read the template, make no card,
don't offer one, and never say a card exists. Nothing in the text changes.

To make the card:

1. Read [passport-card.html](passport-card.html) from this skill's folder.
2. Replace only the JSON between `<!-- MODO-DATA-START -->` and
   `<!-- MODO-DATA-END -->`; change nothing else in the file. The JSON holds
   exactly these fields and no others:
   `{"chat": "<the same words as the opening line, e.g. this chat>",
   "capabilities": [five objects in rubric order, each {"name": "<capability
   name>", "level": 1-5 or "not_shown", "confidence": "low|medium|high"}
   (omit confidence for not_shown)], "evidence": [one or two objects
   {"capability": "<name>", "quote": "<exact quote>"}]}`.
3. The levels, confidences and quotes are the ones from step 2, exactly as
   the text answer will show them, with the quotes copied exactly (the card is
   not a place for new evidence). Pick the one or two strongest quotes. Never put a number out of
   100 in the data: the card turns levels into rings itself using the
   rubric's bands. A "not_shown" capability is shown as "Not shown" with an
   empty ring, never as a zero.
4. Escape the JSON properly (quotes, backslashes, newlines as `\n`) and write
   `<` for any `<` inside a quote so it cannot end the data block.
5. Show the whole filled file with the artifact tool. Don't save it anywhere
   else and add no network calls, badges or extra text to it. The label is
   already in the template.

Then write the text answer (step 4). If the card was created, the text
answer has one more plain sentence, just before the label (after the export
sentence): "I also made a card of this result." Never say the card is
verified or official.

## 4. Write the answer

Plain text that reads well in a terminal. No tables. Keep to this shape:

```
Assessment of <which chat> (<n> messages from you), against Modo rubric v1.

Problem Solving: Level 3 of 5 (confidence: medium)
  Evidence: "<exact quote>"; "<exact quote>"
  Next level: <one line>

Verification: Level 4 of 5 (confidence: high)
  Evidence: ...
  Next level: ...

Workflow Design: Not shown in this chat
  Next level: <what a chat would show to be scored>

Delegation: ...
Strategic Thinking: ...

<the label>
```

- The opening line always says which chat or file was assessed, in these
  forms: "this chat", "the chat you pasted", `your chat "<title>" (<date>)`
  from an export or a past chat, or "the Claude Code session file <name>".
  Use the same words in the too-short message.
- If the user asked for several chats or an overall picture, add one line
  right after the opening line: "I assess one chat at a time, so this covers
  only this chat." Say nothing else about other chats.
- Use "Level N of 5" so it is clear what the number is. Don't convert levels
  to a score out of 100 in this text.
- Add no summary verdict. The full order of the answer is always:
  1. the opening line;
  2. the one-chat line, only if the user asked for several chats;
  3. the five capability blocks;
  4. the improvements section, ending with the skill offer (step 5), when at
     least one capability was shown;
  5. the export sentence (end of step 5);
  6. the card sentence, only if a card was made (step 3);
  7. the label, last (step 7).

## 5. Improvements

Right after the five blocks, add this section so the user can act on the
score. It uses the same chat and the same rubric file; it is not scored and
adds no new evidence. The too-short, "which one?", "can't open it" and "no
chat with that name" messages have no improvements section.

**Choose the two weakest capabilities that were shown.**
1. Take only capabilities with a level 1 to 5. **Never choose a "not shown"
   one**: there is nothing to improve from, and no technique or prompt for it
   appears anywhere in the section.
2. Rank by level, lowest first.
3. Tie on level: the one with the **higher confidence** goes first (a firmly
   shown weakness is the better thing to work on than a doubtful one). Still
   tied: take the earlier one in rubric order (Problem Solving, Verification,
   Workflow Design, Delegation, Strategic Thinking).
4. If only one capability was shown, improve that one. If none, skip this
   section (and the skill offer) and go straight to the label.

Write it in this shape, once per chosen capability:

```
Improvements

1. <Capability> (Level N of 5 now)
   Technique: <what to do differently, taken from the rubric's next level up>
   Try this next time: "<a prompt the user can copy and paste as it stands>"

2. <Capability> ...
```

- The **technique** is the step to the next level of that capability in the
  rubric file, in its terms and tied to this chat (for example the moment you
  quoted). For level 5, say how to keep it up. No generic advice ("be
  clearer") that you can't trace to a line of the rubric.
- The **prompt** is written to Claude, ready to paste, using this user's own
  subject matter from the chat where it helps. Fill in every goal, decision,
  number and name the chat already shows; a bracketed slot is only for a fact
  the chat does not contain and only the user can supply (such as pasted
  data), and no prompt should need more than one.

Then end the section with one offer, as a question: do they want these turned
into one reusable skill they can keep. Say that nothing is saved unless they
choose. Create nothing yet.

After that offer (or, when there is no improvements section, after the five
blocks) add one plain sentence, not a question: they can also ask you to
export this assessment as a report, and nothing is written unless they ask.

## 6. When the user answers the offer

- **No, or no reply about it.** Accept in one line. Don't draft anything.
- **Yes.** Build one skill that applies both techniques (the instructions hold
  the technique and the prompt for each capability, in the user's own subject
  area). Use the first of these that is available:
  1. A tool that proposes a skill for the user to save (claude.ai shows it as
     a "Save skill" card). The user still decides by saving or dismissing it.
  2. A skill-creator skill: hand it the techniques and prompts.
  3. Otherwise write the complete skill here in the chat: a front matter
     block with `name` (lowercase, hyphens) and a `description` saying when
     to use it, then the instructions. Tell them to save it as a skill from
     Claude's skills settings.
  Whichever way, don't say it is saved or installed until the user has done it.

## 7. The label

Every response from this skill, including the too-short message, any "which
one?", "can't open it" or "no chat with that name" message, and the reply to
the skill offer (step 6), ends with this line exactly, on its own line, after everything else (including the
improvements and the offer):

Self-assessment by Claude using Modo rubric v1 — not verified.
