---
formatVersion: "0.1"
id: Q-005
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

# How should Mutation Transaction history be stored and retained?

## Claims

### C1

It remains undecided whether the history needed for Undo, audit, and explanation belongs in Product Model files, a separate append-only log, Git commits, application metadata, or some combination.

```product-claim
review:
  state: questioned
```

### C2

The selected history design must preserve file authority without forcing coding agents to consume operational history they do not need.

```product-claim
review:
  state: questioned
```

## Relationships

### R1

```product-relationship
type: related
target: DEC-002
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: SUB-040
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: SUB-050
review:
  state: confirmed
```
