---
formatVersion: "0.1"
id: CAP-060
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

# Preserve optional interface references

## Claims

### C1

The user can record how closely future implementations should preserve the Source Prototype's appearance.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:ae4e2d684d1fb3194a60199a15cb2556dbffb809164d935a0ce1855d8c2a9c3c
```

### C2

Screens or individual regions can have exact, structural, adaptive, inspirational, or unspecified Preservation Policies.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:12282929951fa7c71512b04b5d6f23349ea7a14bf725c1e36a56e2b9fc036674
```

### C3

Evidence for a Preservation Policy may include screenshots, render profiles, design tokens, assets, component states, and selected source references.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a4e4480abec575b73d89d98aef681e2ff20817f2a14f6530d601984413dee52e
```

### C4

Appearance information supplements behavioral intent rather than replacing it.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a5c8a32afb217d54d5f3c1cae0257ce61d1598b31c7b08862de80630cd86fe9e
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
target: SUB-030
review:
  state: confirmed
```
