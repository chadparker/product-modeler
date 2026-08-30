---
id: CAP-030
type: capability
title: Resolve consequential uncertainty
parent: CAP-001

defaults:
  review: confirmed
  basedOn:
    - SRC-001
---

# Resolve consequential uncertainty

The user and AI refine a provisional Product Model through an adjacent conversation. The system identifies ambiguity and translates conclusions into structured changes while preserving traceability and user control.

## Claims

### C1 — Clarification Questions do not block creation of the first provisional model

- Review: inherited
- Based on: inherited

### C2 — Questions are prioritized by expected downstream impact

- Review: inherited
- Based on: inherited

### C3 — Balanced is the default Mutation Mode

- Review: inherited
- Based on: `DEC-002`

### C4 — Every applied Mutation Transaction is summarized and supports atomic Undo

- Review: inherited
- Based on: `DEC-002`

## Relationships

### R1 — Requires `SUB-020`

- Type: `requires`
- Review: inherited
- Based on: inherited

### R2 — Requires `SUB-040`

- Type: `requires`
- Review: inherited
- Based on: inherited
