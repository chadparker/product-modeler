---
formatVersion: "0.1"
id: CAP-070
type: capability
parent: CAP-001
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Hand the Product Model to external coding agents

## Claims

### C1

The user can point an external coding agent at the Product Model directory without requiring Product Modeler to generate application code.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f4d3e1ef582dcdca3a39bb3b6b80b7989bab736a645d0d5aa2b56ebb928372dc
```

### C2

The Product Model identifies authoritative behavior, unresolved uncertainty, optional appearance requirements, and implementation constraints while remaining neutral about the coding agent and implementation stack.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:2d86528f919d1a34759065514571c3c07c0fef264bf70e440a6f079effbbaa52
```

## Relationships

### R1

```product-relationship
type: requires
target: CAP-040
review:
  state: confirmed
```
