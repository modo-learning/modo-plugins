---
type: regex
pattern: 'Level\s*[1-5]\b|\b[1-5]\s*(?:/|of)\s*5\b|\b\d{1,3}\s*/\s*100\b|confidence:'
flags: i
match: not_contains
target: last_message
---
