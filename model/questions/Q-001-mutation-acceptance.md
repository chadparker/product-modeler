---
formatVersion: "0.1"
id: Q-001
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

# Must AI mutations be accepted before writing files?

## Context

Resolved by [`DEC-002`](../decisions/DEC-002-configurable-atomic-mutations.md).

## Claims

### C1

Every AI-generated change is an atomic, validated Mutation Transaction, and projects support Fast, Review Everything, and Balanced Mutation Modes.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f95c93014bfe7e334f8c5954bfe68c45e6d8c16415c8a4eacffd2c2d827ce0d7
```

### C2

Balanced is the default: provisional and explicit structured user changes apply immediately, while AI-generated changes to confirmed or foundational intent require approval; every applied transaction produces a visible summary and supports Undo.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:5020c5df5e15bdbc2001bbe9cd87f6c1ef6f98a58a2c1d1e95c2e7bd04c6ffd5
```

## Relationships

### R1

```product-relationship
type: resolvedBy
target: DEC-002
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: CAP-030
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: SUB-040
review:
  state: confirmed
```
