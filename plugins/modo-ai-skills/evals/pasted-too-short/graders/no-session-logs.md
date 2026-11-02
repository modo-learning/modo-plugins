---
type: regex
pattern: 'session logs?|transcripts? of your coding|\.claude/projects|~/\.claude|claude code sessions?'
flags: i
match: not_contains
target: last_message
---
