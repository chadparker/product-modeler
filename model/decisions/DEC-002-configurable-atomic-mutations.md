---
id: DEC-002
type: decision
title: Use configurable atomic mutation policies
status: accepted
date: 2026-08-29
resolves:
  - Q-001
related:
  - CAP-030
  - SUB-040
---

# Use configurable atomic mutation policies

Every AI-generated Product Model change is an atomic, validated Mutation Transaction with a trigger, rationale, affected entities, before-and-after values, and Undo support.

Projects offer three Mutation Modes:

- `fast` — apply every valid AI transaction immediately;
- `review-everything` — stage every AI transaction;
- `balanced` — immediately apply provisional and explicit structured user changes while staging changes to confirmed or foundational intent.

Balanced is the default and uses visible deterministic protection rules rather than an opaque risk score.

See [`../../docs/adr/0004-configurable-atomic-mutations.md`](../../docs/adr/0004-configurable-atomic-mutations.md).
