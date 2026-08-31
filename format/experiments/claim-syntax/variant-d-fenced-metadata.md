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

### C1

Clarification Questions do not block creation of the first provisional model.

### C2

Questions are prioritized by expected downstream impact.

### C3

Balanced is the default Mutation Mode.

```product-claim
provenance:
  basedOn:
    add:
      - DEC-002
```

### C4

Every applied Mutation Transaction is summarized and supports atomic Undo.

```product-claim
provenance:
  basedOn:
    add:
      - DEC-002
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-020
```

### R2

```product-relationship
type: requires
target: SUB-040
```
