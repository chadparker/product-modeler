---
formatVersion: "0.1"
id: CAP-010
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

# Ingest product evidence

## Claims

### C1

The user can supply prose specifications, source repositories, or both as Product Evidence about a software product.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:62fa2edd0f464109ad5670ad0941ae2e5585c1b33ad29c467e1f57ccbef1fed7
```

### C2

Initial ingestion supports prose and outline specifications, local web-application source repositories, and optional runtime inspection when the application can be executed.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:5712fea4f973866a15e07f16ace57246b141fe8dbd84ced95c645e597a18e9e1
```

### C3

The system inventories inputs with enough identity and location information for later Claims to cite them.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:3373f36d931b68bc02cd1bad19a03f3006e165d5f94d5c8877d6814fc9d4e6c5
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-010
review:
  state: confirmed
```
