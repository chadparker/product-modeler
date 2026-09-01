---
formatVersion: "0.1"
id: Q-007
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

# How should confirmed Claims become stale after content changes?

## Context

Resolved by [`DEC-004`](../decisions/DEC-004-adopt-d-plus.md). See [`../../format/DPLUS.md`](../../format/DPLUS.md) for the normative digest algorithm.

## Claims

### C1

Confirmed Claims store a SHA-256 digest of normalized normative Claim Markdown, and validation reports stale confirmation when current content does not match the recorded digest.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:771af8c4ad1fd7e6111e32dfb48a8e6c4a09d211bb62a46440cb1158674e58ce
```

### C2

Confirmed state and content digests cannot be inherited from entity defaults.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:37c518ac9a19971ab35c62e4c4cbbd3181c753ece8e55952d0c20c6b055237e0
```

## Relationships

### R1

```product-relationship
type: resolvedBy
target: DEC-004
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: DEC-003
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: Q-006
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

### R5

```product-relationship
type: related
target: SUB-060
review:
  state: confirmed
```
