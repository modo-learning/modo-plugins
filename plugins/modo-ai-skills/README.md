# Modo AI Skills

Modo AI Skills assesses how well you work with AI in a Claude chat, against
Modo's public rubric. For each of five capabilities (Problem Solving,
Verification, Workflow Design, Delegation, Strategic Thinking) you get a level
from 1 to 5, or "not shown", a confidence label, a quote from your own
messages as evidence, and what the next level looks like.

This is a pre-release stub. The full README (what it reads, what it sends,
install steps) comes with a later release.

## Install

```
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-ai-skills@modo-plugins
```

## Use it

Ask "how good am I at using AI?" or "assess this chat", or in Claude Code run
`/modo-ai-skills:assess-my-ai-work`. It reads only the chat you are in, and
needs at least 4 messages from you to give scores.

In claude.ai and Cowork, Claude can also show the result as a card (five
rings, confidence, top quotes, the self-assessment label). A capability the
chat did not show appears as "Not shown" with an empty ring, not as zero. In
Claude Code the result stays plain text. A sample is in
[docs/passport-card-sample.png](docs/passport-card-sample.png).

After the scores, the assessment names your two weakest shown capabilities
and gives each a technique and a prompt to try next time, then offers (only
offers) to turn them into a reusable skill. To work on one capability without
an assessment, ask "how do I get better at verification?" or run
`/modo-ai-skills:help-me-improve`.

## Export a report

After an assessment, ask "export this" (or run
`/modo-ai-skills:export-assessment`). Claude first proposes up to 5 quotes from
your own messages, a title and a date, and you approve, drop quotes or choose
scores only. It then shows the exact report; nothing is written until you ask.
The report is Markdown, readable on its own, and ends with one machine-readable
block with only: rubric version, the five levels and confidence, the quotes you
approved, the title and the date. No transcript is included. A PDF is made only
if you ask and only if Claude can create files in your session. The exact shape
is in [skills/export-assessment/RECORD.md](skills/export-assessment/RECORD.md).

## The rubric

The rubric is public and versioned:
[skills/assess-my-ai-work/rubric-v1.md](skills/assess-my-ai-work/rubric-v1.md).
The help-me-improve skill keeps an identical copy so each skill folder is
self-contained; `python3 scripts/check_rubric_sync.py plugins/modo-ai-skills`
fails if the two differ. Every result is labelled "Self-assessment by Claude using Modo rubric v1 — not
verified."

## License

MIT. See [LICENSE](LICENSE).
