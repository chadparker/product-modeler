---
id: CAP-030
type: capability
title: Resolve consequential uncertainty
parent: CAP-001
status: confirmed
relations:
  requires:
    - CAP-020
    - SUB-020
    - SUB-040
---

# Resolve consequential uncertainty

The user and AI refine the provisional Product Model through an adjacent conversation.

The system identifies ambiguity, prioritizes questions by expected downstream impact, and translates answers into explicit structured model mutations.

## Important behavior

- Questions do not block the first provisional model.
- Changes caused by an answer are visible and reviewable.
- Rejected Inferences remain traceable without cluttering the active model.
