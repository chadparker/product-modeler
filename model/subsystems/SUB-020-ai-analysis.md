---
formatVersion: "0.1"
id: SUB-020
type: subsystem
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# AI analysis and question prioritization

## Claims

### C1

The subsystem reasons over Product Evidence and the current Product Model to construct provisional entities and relationships.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:aac8c78358d72fdebe42e166b553fb7741aa3cffd41c37f9ae0d854bece7aa69
```

### C2

The subsystem identifies uncertainty and ranks Clarification Questions by expected downstream impact.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:9eb770b92dae4f3a0a3908ed404667c327336c4d37781200526bf559d29b2cd5
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-030
review:
  state: confirmed
```
