---
formatVersion: "0.1"
id: CAP-050
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

# Explore and refine the Product Model

## Claims

### C1

The user can explore the product through a Capability hierarchy with dependency links and an adjacent clarification conversation.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:7ef6c7430adea7cca89afd4107813a4b948e3cb9ded8cc6117a69de714c4286c
```

### C2

The Capability hierarchy is the primary overview of the Product Model.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:3086d0843e576957c00b401725a3dc83276a19577e15582c1b52209da25a8392
```

### C3

Selecting an entity reveals its definition, relationships, evidence, and unresolved questions.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f41984a2ac3d1b011c6c92c277bf9326a2d29e6fb59545f9887458ba2875de57
```

### C4

The user can collapse branches to preserve readability.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:b34785d7f53a4672a06805092999b08158e28ae0b47702a905f5f57dc9bb2675
```

### C5

The workspace highlights changes resulting from clarification conversation.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:7644225d8533a3929c174b45f2ebad890c2e0f9e666808627773c2ca05217676
```

### C6

The user can manually correct the Product Model.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:d6f8c0fe8a33c4064478d5d2eb9ce7e804cbf0e2ce33b8ac9fb363f9e8a36fb9
```

## Relationships

### R1

```product-relationship
type: requires
target: CAP-040
review:
  state: confirmed
```

### R2

```product-relationship
type: requires
target: SUB-040
review:
  state: confirmed
```

### R3

```product-relationship
type: requires
target: SUB-060
review:
  state: confirmed
```
