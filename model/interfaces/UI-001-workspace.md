---
formatVersion: "0.1"
id: UI-001
type: interface
status: inferred
preservation: adaptive
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Product modeling workspace

## Context

The exact workspace composition remains subject to interface validation; these Claims capture the current target direction.

## Claims

### C1

The primary workspace places the Capability hierarchy and clarification conversation side by side.

```product-claim
review:
  state: proposed
```

### C2

Source material is available in a collapsible region, and selecting an entity opens an inspector showing its definition, relationships, evidence, status, and unresolved questions.

### C3

The workspace provides regions for Product Evidence, the Capability hierarchy, clarification conversation, and the entity inspector.

### C4

The workspace visibly distinguishes awaiting input, analyzing, provisional model ready, clarification pending, changes proposed, and model inconsistent states.

```product-claim
review:
  state: questioned
```

## Relationships

### R1

```product-relationship
type: capabilities
target: CAP-030
```

### R2

```product-relationship
type: capabilities
target: CAP-050
```
