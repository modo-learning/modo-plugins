---
type: llm
weight: 1
---

PASS if the response contains a Markdown report that can be understood without the chat: a title naming the session, the label "Self-assessment by Claude using Modo rubric v1 — not verified.", the five capabilities each with a level (or "Not shown") and a confidence, a section listing the approved quotes, and a final section headed as the machine-readable assessment record. A short line before the report about saving a file or not being able to is fine.
FAIL if any of those is missing or the report only makes sense with the chat.
