---
error: true
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
  evidence.0.quote: /^.{1,240}$/s
  evidence.0.capability: [problem_solving, verification, workflow_design, delegation, strategic_thinking]
  evidence.1.quote: /^.{1,240}$/s
  evidence.1.capability: [problem_solving, verification, workflow_design, delegation, strategic_thinking]
  evidence.2.quote: /^.{1,240}$/s
  evidence.2.capability: [problem_solving, verification, workflow_design, delegation, strategic_thinking]
  evidence.3.quote: /^.{1,240}$/s
  evidence.3.capability: [problem_solving, verification, workflow_design, delegation, strategic_thinking]
  evidence.4.quote: /^.{1,240}$/s
  evidence.4.capability: [problem_solving, verification, workflow_design, delegation, strategic_thinking]
---
Input validation error: Invalid arguments for tool save_assessment: rubric_version: must be a rubric version this server knows ("v2")
