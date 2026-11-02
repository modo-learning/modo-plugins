---
type: llm
weight: 3
focus: mock_calls
---

Judge only the input of the save_assessment call(s) shown. The tool's answer (output, isError, verdict) does not matter here, even when it is an error.
PASS if ALL hold: (1) there is exactly one save_assessment call; (2) its input has exactly the top-level fields rubric_version, capabilities, evidence, session_title, session_date and no others (not wrapped in another object); (3) rubric_version is "v1.1" and capabilities has exactly the keys problem_solving, verification, workflow_design, delegation, strategic_thinking, each with only level (an integer 1 to 5 or "not_shown") and confidence ("low", "medium" or "high"); (4) evidence is a list of exactly 0 items, each with only capability (one of the five keys) and quote (a short excerpt, at most 240 characters, not a transcript or summary); (5) session_title is a short title of at most 120 characters and session_date a yyyy-mm-dd date.
FAIL otherwise.
