---
type: regex
pattern: '"(transcript|messages|conversation|chat|history|summary|improvements|next_level|prompts?)"\s*:'
target: mock_calls
match: "not_contains"
---
