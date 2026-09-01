---
formatVersion: "0.1"
id: DEC-003
type: decision
status: accepted
date: 2026-08-30
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Use inherited claim-level provenance

## Context

See [`../../docs/adr/0005-inherited-claim-provenance.md`](../../docs/adr/0005-inherited-claim-provenance.md) for the architectural rationale.

## Claims

### C1

Entities provide Provenance Defaults inherited by their contained Claims.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:2aa9b0bee4632c01c25a18dcca0573de7f39711b0342eaf12dc604d17aac8bdb
```

### C2

Consequential Claims receive stable local IDs, override inherited defaults only where necessary, and are addressed using their entity ID and local ID, such as `CAP-030#C3`.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:fdb5bb06571506b2a1701ab53cafe349c939ca45ee1b1498eaccee7b3ed241a0
```

### C3

Consequential relationships may receive local IDs, while ordinary explanatory prose does not require Claim metadata.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f5480f40f1bb50baf63d5272e91869ef92a033cf91911377d9bacfc078a738b7
```

### C4

The UI supports both bulk entity review and individual Claim review.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:02daf25d5af7a6dc9af67643ca706b851f067a6d8a38c64d6d9403d211d29503
```

## Relationships

### R1

```product-relationship
type: resolves
target: Q-002
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
