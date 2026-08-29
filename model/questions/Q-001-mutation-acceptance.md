---
id: Q-001
type: question
title: Must AI mutations be accepted before writing files?
status: resolved
resolvedBy: DEC-002
impact: high
related:
  - CAP-030
  - SUB-040
---

# Must AI mutations be accepted before writing files?

## Resolution

Every AI-generated change is an atomic, validated Mutation Transaction. Projects support Fast, Review Everything, and Balanced Mutation Modes. Balanced is the default: provisional and explicit structured user changes apply immediately, while AI-generated changes to confirmed or foundational intent require approval.

All applied transactions produce a visible summary and support Undo.

See [`../decisions/DEC-002-configurable-atomic-mutations.md`](../decisions/DEC-002-configurable-atomic-mutations.md).
