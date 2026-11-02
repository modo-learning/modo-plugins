---
type: regex
pattern: 'session log|transcript|\.jsonl|~/\.claude'
flags: i
match: not_contains
target: last_message
---
