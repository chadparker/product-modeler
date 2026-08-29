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

The system identifies ambiguity, prioritizes questions by expected downstream impact, and translates answers into atomic, validated Mutation Transactions.

## Important behavior

- Questions do not block the first provisional model.
- Fast, Review Everything, and Balanced Mutation Modes are available per project.
- Balanced is the default and protects confirmed or foundational intent.
- Every applied transaction is summarized and supports Undo.
- Rejected Inferences remain traceable without cluttering the active model.
