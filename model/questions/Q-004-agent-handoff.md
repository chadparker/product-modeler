---
formatVersion: "0.1"
id: Q-004
type: question
status: unknown
impact: medium
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# What is the minimum useful external-agent handoff contract?

## Claims

### C1

The external-agent handoff format should ideally be self-explanatory.

```product-claim
review:
  state: proposed
```

### C2

It remains unknown whether an external coding agent can correctly identify authoritative requirements, unresolved questions, dependencies, and appearance policies from self-explanatory Product Model files without a dedicated skill.

```product-claim
review:
  state: questioned
```

## Relationships

### R1

```product-relationship
type: related
target: CAP-070
review:
  state: confirmed
```
