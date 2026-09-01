---
formatVersion: "0.1"
id: Q-002
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

# Should provenance attach to entities or individual Claims?

## Context

Resolved by [`DEC-003`](../decisions/DEC-003-inherited-claim-provenance.md).

## Claims

### C1

Entities provide Provenance Defaults inherited by their contained Claims, while consequential Claims and relationships receive stable local IDs and override defaults only where necessary.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f5f980ae9ff1987dada82fa801037a4c4e5a20ff1b7d3df89f841b871bfb80e3
```

### C2

Ordinary explanatory prose remains unannotated, and a Claim is addressed using its entity ID and local ID, such as `CAP-030#C3`.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:e3a77da3ce5a5405cd602a3e23086cf639691cd9308ba635fe066bdbb0069ae3
```

## Relationships

### R1

```product-relationship
type: resolvedBy
target: DEC-003
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: SUB-030
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: CAP-040
review:
  state: confirmed
```
