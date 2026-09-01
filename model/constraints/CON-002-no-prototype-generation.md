---
formatVersion: "0.1"
id: CON-002
type: constraint
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Product Modeler does not generate product implementations

## Claims

### C1

Product Modeler ends at the structured Product Model and does not generate product implementations.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:3d91cb31eca62b8aeba5909f5874afaa48fe7b2d9c36c5b9c7a1d1cc84a2c710
```

### C2

Users may hand the Product Model to any external coding agent or development process.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:0175cf07237bc39fcb779e7656078408ba094af88cafbd802373969ad22e86dd
```

## Relationships

### R1

```product-relationship
type: appliesTo
target: PROD-001
review:
  state: confirmed
```
