---
formatVersion: "0.1"
id: CON-001
type: constraint
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Initial analysis targets web applications

## Claims

### C1

The first version analyzes web-application prototypes.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:1bd2eb2c6463ad330296309cc09a8e14a7b7a5c2a045fa23baeebf5da219a9da
```

### C2

The Product Model must remain extensible to mobile and desktop products without requiring the initial analyzer to support them.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:d1053887107171a3ba94f67e14c436edaf70b27d1956cc8af432333b1409ca38
```

## Relationships

### R1

```product-relationship
type: appliesTo
target: CAP-010
review:
  state: confirmed
```

### R2

```product-relationship
type: appliesTo
target: CAP-020
review:
  state: confirmed
```
