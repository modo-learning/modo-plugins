---
type: regex
pattern: '```json|"rubric_version"|# Modo AI Skills assessment|\|\s*Capability\s*\|'
flags: i
match: not_contains
target: last_message
---
