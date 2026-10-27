---
expect:
  rubric_version: v1
  session_title: /^.{1,120}$/s
  session_date: /^\d{4}-\d{2}-\d{2}$/
  evidence: array
  capabilities.problem_solving.level: ["1", "2", "3", "4", "5", not_shown]
  capabilities.problem_solving.confidence: [low, medium, high]
  capabilities.verification.level: ["1", "2", "3", "4", "5", not_shown]
  capabilities.verification.confidence: [low, medium, high]
  capabilities.workflow_design.level: ["1", "2", "3", "4", "5", not_shown]
  capabilities.workflow_design.confidence: [low, medium, high]
  capabilities.delegation.level: ["1", "2", "3", "4", "5", not_shown]
  capabilities.delegation.confidence: [low, medium, high]
  capabilities.strategic_thinking.level: ["1", "2", "3", "4", "5", not_shown]
  capabilities.strategic_thinking.confidence: [low, medium, high]
---
Saved assessment 3f6c2a1e-8d4b-4c7a-9e2f-1b5d7a9c0e42: "{{input.session_title}}" ({{input.session_date}}).
