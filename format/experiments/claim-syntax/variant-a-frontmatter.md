---
id: CAP-030
type: capability
title: Resolve consequential uncertainty
parent: CAP-001

defaults:
  review: confirmed
  basedOn:
    - SRC-001

claims:
  - id: C1
    statement: Clarification Questions do not block creation of the first provisional model.

  - id: C2
    statement: Questions are prioritized by expected downstream impact.

  - id: C3
    statement: Balanced is the default Mutation Mode.
    basedOn:
      - DEC-002

  - id: C4
    statement: Every applied Mutation Transaction is summarized and supports atomic Undo.
    basedOn:
      - DEC-002

relationships:
  - id: R1
    type: requires
    target: SUB-020

  - id: R2
    type: requires
    target: SUB-040
---

# Resolve consequential uncertainty

The user and AI refine a provisional Product Model through an adjacent conversation. The system identifies ambiguity and translates conclusions into structured changes while preserving traceability and user control.

## Notes

The authoritative behavioral statements live in frontmatter. This prose provides context but must not silently introduce additional requirements.
