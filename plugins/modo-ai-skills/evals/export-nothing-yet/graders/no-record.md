---
type: regex
pattern: '```json|"rubric_version"|Level\s*[1-5]\b'
flags: i
match: not_contains
target: last_message
---
