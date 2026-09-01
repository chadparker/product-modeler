---
formatVersion: "0.1"
id: SUB-040
type: subsystem
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Clarification conversation and structured mutations

## Claims

### C1

The subsystem maintains contextual conversation beside the Product Model and converts conclusions into atomic, validated create, update, move, relate, reject, and resolve Mutation Transactions.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:88b9523f397b1e23f89075d8e083c3a909eee6c0fe0f31575cad53944e2e66a9
```

### C2

The subsystem enforces the active Fast, Review Everything, or Balanced Mutation Mode and exposes staged changes for approval.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:35affe62e9528270a88ef79b1cbc9b3293566b5b00639f589895b994dd0e5111
```

### C3

The subsystem summarizes applied changes and supports atomic Undo.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:cfbe48de40d3851c66338a2a67fafcfea6a4b0ff9668825f0f0e71c3414f85da
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-020
review:
  state: confirmed
```

### R2

```product-relationship
type: requires
target: SUB-060
review:
  state: confirmed
```
