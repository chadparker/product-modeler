---
formatVersion: "0.1"
id: CAP-020
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

# Infer product intent and behavior

## Claims

### C1

The system constructs a useful provisional Product Model from incomplete Product Evidence.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:43bb8c151122c88f4d3427cc2e6db1589ba718395ccba76f8daaed552d21c2fc
```

### C2

The system records source behavior as Observations, groups related Observations into Candidate Behaviors, and initializes Target Dispositions according to the selected Import Strategy.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:6affe71d9bb362f66db4325d5b7cf90daf7355089b32b9758d97a2012e149c1e
```

### C3

The system infers the Product Frame, identifies the Core Capability and Supporting Capabilities, and reconstructs Journeys.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a4e43bd78f1ff7a0dbcf01f9d2a6ffb8681f3fbf1c3bfa3377b8b141092fe8ee
```

### C4

The system identifies Domain Concepts, rules, transitions, Interfaces, important Interface States, shared Subsystems, and dependencies.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:cbd61e2fd089b5c3a310d950767697ab6adc6a912b941c6e7e3bd3ebf22de071
```

### C5

The system retains evidence and uncertainty for consequential conclusions and produces a provisional model before exhaustive clarification.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:985dbe195294b26ac6b9ae50ed886862b79b2ab4b28c3fbe705b8b83cac57fb1
```

## Relationships

### R1

```product-relationship
type: requires
target: CAP-010
review:
  state: confirmed
```

### R2

```product-relationship
type: requires
target: SUB-020
review:
  state: confirmed
```

### R3

```product-relationship
type: requires
target: SUB-030
review:
  state: confirmed
```
