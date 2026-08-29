---
id: Q-005
type: question
title: How should mutation history be stored and retained?
status: unknown
impact: medium
related:
  - DEC-002
  - SUB-040
  - SUB-050
---

# How should mutation history be stored and retained?

Mutation Transactions need enough history for Undo, audit, and explanation. It remains undecided whether that history belongs in Product Model files, a separate append-only log, Git commits, application metadata, or some combination.

The choice should preserve file authority without forcing coding agents to consume operational history they do not need.
