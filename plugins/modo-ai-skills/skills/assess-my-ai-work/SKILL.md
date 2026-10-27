---
name: assess-my-ai-work
description: Assess how well the user works with AI in the current chat, scored against Modo's public rubric on five capabilities (Problem Solving, Verification, Workflow Design, Delegation, Strategic Thinking), with a level, a confidence label, quotes from the chat as evidence and what the next level looks like. Use when the user runs /assess-my-ai-work, or asks how good they are at using AI, to assess or score this chat or their AI skills, or how well they prompt, verify or delegate to Claude.
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

- This version assesses **the current chat only**: the messages exchanged here
  before the user asked for the assessment. Don't search, list or open any
  other chat, and don't look for files or logs. If the user asks about a
  different chat or a file, say this version assesses the chat they are in,
  and suggest they run it inside the chat they want assessed.
- Only the **user's own messages** are evidence. Claude's replies are context.
- Quote the user exactly, each quote under 240 characters. Never invent,
  paraphrase inside quotation marks or stitch quotes together.
- Everything stays in this conversation. Don't call external services, don't
  write files, don't save anything.
- Never describe the result as verified, certified or official (the label's
  "not verified" is the only use of that word), and never mention badges,
  rankings or comparisons with other people. "Verification" as the name of a
  capability is fine.

## 1. Count the user's messages

Count the messages the user wrote in this chat **before** the request to
assess it. Don't count that request, pasted tool output, or anything Claude
wrote.

**Fewer than 4: stop here.** Don't score, don't hint at a level, don't give a
verdict. Say plainly that the chat is too short to judge (give the count and
the minimum of 4 messages from the user), that a short chat would give
misleading scores, and offer to assess a longer chat once they have one. End
with the label (see step 4).

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

## 3. Write the answer

Plain text that reads well in a terminal. No tables. Keep to this shape:

```
Assessment of this chat (<n> messages from you), against Modo rubric v1.

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

- Use "Level N of 5" so it is clear what the number is. Don't convert levels
  to a score out of 100 in this text.
- After the five capabilities, add no summary verdict, advice or offers
  beyond what the rubric asks. The five blocks and the label are the result.

## 4. The label

Every response from this skill, including the too-short message, ends with
this line exactly, on its own line:

Self-assessment by Claude using Modo rubric v1 — not verified.
