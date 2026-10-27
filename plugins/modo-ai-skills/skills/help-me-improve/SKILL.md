---
name: help-me-improve
description: Help the user get better at ONE named AI-work capability (Problem Solving, Verification, Workflow Design, Delegation or Strategic Thinking) with concrete techniques and copy-ready prompts drawn from Modo's public rubric. Works with no earlier assessment and reads no chat. Use when the user runs /help-me-improve, or asks how to get better at verifying, delegating, framing problems, designing workflows or thinking strategically when working with AI, or how to reach the next level in one of those.
---

# Help me improve

Give practical help with one capability, grounded in Modo's public rubric.
This skill does not assess anyone and does not need a prior assessment.

The rubric is the file [rubric-v1.md](rubric-v1.md) in this skill's folder
(an identical copy of the one used by the assess-my-ai-work skill). **Read it
in full before answering.** Every technique must be traceable to a line in
that capability's level table. No generic tips ("double-check everything",
"be clearer").

## Ground rules

- Do not read, search or open any chat, file or log. The help comes from the
  rubric and from what the user tells you in this message. Do not mention or
  offer coding-tool session logs.
- Give no level, score or confidence for the user. Nothing was assessed. Never
  describe anything as verified or certified, and never mention badges or
  comparisons with other people.
- Add no self-assessment label. That label marks an assessment result, and
  this skill assesses nothing.
- Write nothing to files and save nothing unless the user chooses it (step 4).

## 1. Which capability

Map the user's request to one of the five: Problem Solving, Verification,
Workflow Design, Delegation, Strategic Thinking. Everyday wording is fine
("checking its work" is Verification, "handing tasks over" is Delegation).

- Two or more capabilities named: ask which one to start with, in one short
  message that lists them, then stop.
- None named, or one that is not on the list: say the five and ask which, in
  one short message, then stop.

A short question like these is the whole response: nothing else.

## 2. Where to start

- If the user says what they do today ("I never check", "I sometimes
  spot-check numbers"), match that to the closest level in the rubric table
  for that capability and help with the **next level up**.
- If they don't say, don't guess a level. Give the **two steps from the
  bottom**: how to get to level 3 and then how to get to level 4, labelled
  "Step to level 3" and "Step to level 4". Say they can stop at the one that
  feels new. Level 5 is mentioned in one line as where it leads.
- If they say they already do what level 4 describes, help with level 5. If
  they already do level 5, give ways to keep it up.

## 3. The help

For each step, in this shape:

```
<Capability>: <target, e.g. "Level 4 of 5">

Technique: <what to do differently, in the rubric's terms>
Why it counts: <the rubric line it comes from, in a few words>
Try this next time: "<a prompt to paste to Claude, ready as it stands>"
```

- The prompt is written to Claude, in full sentences. If you know the user's
  subject, use it; if not, use a neutral example and mark the one or two
  words they swap (for example [the figure]).
- Keep it short: one technique and one prompt per step, not a lecture.

Then offer once, as a question, to turn the technique into a reusable skill
they can keep, and say that nothing is saved unless they choose.

## 4. When the user answers the offer

- **No, or no reply about it.** Accept in one line. Don't draft anything.
- **Yes.** Build one skill that applies the technique and the prompt(s) (and
  says when to use it). Use the first of these that is available:
  1. A tool that proposes a skill for the user to save (claude.ai shows it as
     a "Save skill" card). The user still decides by saving or dismissing it.
  2. A skill-creator skill: hand it the technique and prompts.
  3. Otherwise write the complete skill here in the chat: a front matter
     block with `name` (lowercase, hyphens) and a `description` saying when
     to use it, then the instructions. Tell them to save it as a skill from
     Claude's skills settings.
  Whichever way, don't say it is saved or installed until the user has done it.
