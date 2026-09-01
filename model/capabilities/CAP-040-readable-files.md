---
formatVersion: "0.1"
id: CAP-040
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

# Represent the Product Model as readable files

## Claims

### C1

The user obtains an authoritative, Git-friendly Product Model directory that remains understandable without Product Modeler.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:03649ff3210818e8b012a72d50e6b3a9baff201edb16b5e2df95c27c7f1e06af
```

### C2

Product Model entities retain stable IDs across file renames and moves.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:83cd7f945f9d6bb1e950203624d9a4e9ed1afbcb35cdde390e98c3acba58a799
```

### C3

The primary Capability hierarchy and cross-tree dependencies are explicit in the model.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:2082c51ee1937b06b4334f1b6b713f1ebb9280b16245788174ecb6865fd46172
```

### C4

The format records provenance and uncertainty through inherited entity defaults and stable local Claim IDs.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a75cf2aa9c31468a01e78e2c5c393000cac1f96e0ed4aeb8630a7f507ab4a995
```

### C5

The UI and external agents can address Claims using an entity ID and local ID, such as `CAP-030#C3`.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:03b98a3820fa84700f7709202cc3f508bb9beab3c8eb80b25f4c41e6f7387d59
```

### C6

Derived databases and graph indexes are disposable caches that can be rebuilt from authoritative files.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:05cc7b591b42837e783066e87065ce62d70b008e7d43fd9868713b89f6baa592
```

### C7

The Product Model can be validated for structural consistency.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:de257af9ef11646ccd376d0e8840f6104e79a6c3adf29aaafb08b964666cd76b
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-050
review:
  state: confirmed
```

### R2

```product-relationship
type: requires
target: SUB-060
review:
  state: confirmed
```
