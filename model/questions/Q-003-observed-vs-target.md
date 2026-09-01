---
formatVersion: "0.1"
id: Q-003
type: question
status: resolved
impact: high
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# How does the model distinguish the observed product from the intended target?

## Context

A Source Prototype may contain behavior the user wants to remove, while the user may propose behavior not present in the prototype. Resolved by [`DEC-001`](../decisions/DEC-001-observations-candidates-intent.md).

## Claims

### C1

The Product Model separates granular Observations, grouped Candidate Behaviors, and intended Product Model entities.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:0080586a023ef08d0ffd4ad263f19d0a22cfd2cac2b5708393d5a29f06167609
```

### C2

Candidate Behaviors carry an independent Target Disposition and may be initialized through prototype-as-starting-point, empty-target, or review-individually Import Strategies.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:3f12c052e934dc71d9c5c88d0d3786d9b48f92e90dbac10ac6af60880691169c
```

## Relationships

### R1

```product-relationship
type: resolvedBy
target: DEC-001
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: CAP-020
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: CAP-030
review:
  state: confirmed
```

### R4

```product-relationship
type: related
target: SUB-030
review:
  state: confirmed
```
