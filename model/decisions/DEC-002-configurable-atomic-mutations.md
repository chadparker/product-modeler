---
formatVersion: "0.1"
id: DEC-002
type: decision
status: accepted
date: 2026-08-29
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Use configurable atomic mutation policies

## Context

See [`../../docs/adr/0004-configurable-atomic-mutations.md`](../../docs/adr/0004-configurable-atomic-mutations.md) for the architectural rationale.

## Claims

### C1

Every AI-generated Product Model change is an atomic, validated Mutation Transaction with a trigger, rationale, affected entities, before-and-after values, and Undo support.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:b4aa5e9d4b0d8af5c31b909cd4b6ecfe7992650fb7874041164cedcd4c3b1011
```

### C2

Projects offer Fast Mode, which applies every valid AI transaction immediately; Review Everything Mode, which stages every AI transaction; and Balanced Mode, which immediately applies provisional and explicit structured user changes while staging changes to confirmed or foundational intent.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:e2bf68be6a3a385663e439bf41d6161794ee38446a56ade076647081b7b746d6
```

### C3

Balanced Mode is the default and uses visible deterministic protection rules rather than an opaque risk score.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:34717033228fc451d9f5d000c4ebff9eebdc7dcf15aca5a451445b2192beafd9
```

## Relationships

### R1

```product-relationship
type: resolves
target: Q-001
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
