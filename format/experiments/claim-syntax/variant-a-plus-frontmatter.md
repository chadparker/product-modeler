---
formatVersion: "0.1-experiment"
id: CAP-030
type: capability
title: "Resolve consequential uncertainty"
parent: CAP-001

defaults:
  review: confirmed
  provenance:
    basedOn:
      - SRC-001

claims:
  C1:
    statement: "Clarification Questions do not block creation of the first provisional model."

  C2:
    statement: "Questions are prioritized by expected downstream impact."

  C3:
    statement: "Balanced is the default Mutation Mode."
    provenance:
      basedOn:
        add:
          - DEC-002

  C4:
    statement: "Every applied Mutation Transaction is summarized and supports atomic Undo."
    provenance:
      basedOn:
        add:
          - DEC-002

relationships:
  R1:
    type: requires
    target: SUB-020

  R2:
    type: requires
    target: SUB-040
---

## Context

The user and AI refine a provisional Product Model through an adjacent conversation. The system identifies ambiguity and translates conclusions into structured changes while preserving traceability and user control.

All normative Claims and relationships are represented exactly once in YAML frontmatter. This Markdown section is non-normative context.
