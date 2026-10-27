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

## The rubric

The rubric is public and versioned:
[skills/assess-my-ai-work/rubric-v1.md](skills/assess-my-ai-work/rubric-v1.md).
Every result is labelled "Self-assessment by Claude using Modo rubric v1 — not
verified."

## License

MIT. See [LICENSE](LICENSE).
