---
id: Q-003
type: question
title: How does the model distinguish the observed product from the intended target?
status: resolved
resolvedBy: DEC-001
impact: high
related:
  - CAP-020
  - CAP-030
  - SUB-030
---

# How does the model distinguish the observed product from the intended target?

A Source Prototype may contain behavior the user wants to remove, while the user may propose behavior not present in the prototype.

## Resolution

The model separates granular Observations, grouped Candidate Behaviors, and intended Product Model entities. Candidate Behaviors carry an independent Target Disposition and may be initialized through prototype-as-starting-point, empty-target, or review-individually import strategies.

See [`../decisions/DEC-001-observations-candidates-intent.md`](../decisions/DEC-001-observations-candidates-intent.md).
