---
formatVersion: "0.1"
id: JRN-001
type: journey
status: confirmed
participants:
  - product-owner
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Recover and clarify a product from source code

## Context

This Journey exercises the representative path from source-code evidence to an agent-ready Product Model.

## Claims

### S1

The user supplies a small web-application repository.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:494b112cf005fe4a34f75fa05abe9a48cfcd744a3f39a6091480c3d594f5c0c6
```

### S2

The system inventories the repository as Product Evidence.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:5d3d021d14c1c285b73fd5786b11a70c9d04138e27906beef03e69ab98ac2293
```

### S3

The AI constructs a provisional Product Frame and Capability hierarchy.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:30c49d54eeeb3734497f27088925fadc2330d1c8e0e9ac6b742ea7e71dec95fd
```

### S4

The user explores Product Model entities and their evidence.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:4c605aa1d49066ee94ba56ef1bcb0804ff6a782e5af359fb28560a75b8b73571
```

### S5

The AI asks the highest-impact Clarification Question.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:19dff67bd5eeab1ee137ef4d439b2e8abea1aa95f71acaceac6be7471fa63b32
```

### S6

The user answers the Clarification Question through the adjacent conversation.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:fb2ee9e7f83d197a6b6717f033dc6283b425696533734520edc43d34622c2113
```

### S7

The AI proposes Mutation Transactions that encode structured changes derived from the answer.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:1af5190eca1e783d683e02920502644a68dddc5f014a6c89efd91030767e59be
```

### S8

Accepted changes update both the authoritative files and their derived visual projections.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:409484d4fdd8248c6ac4d8d2131398552bac5575d02b3c6206f41578bfe22f73
```

### S9

The user hands the Product Model directory to an external coding agent.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:7018214fcc89d75462a65293f9fbc2c40f97f4ad26990c3fac6ab2d7fa172edd
```

## Relationships

### R1

```product-relationship
type: capabilities
target: CAP-010
review:
  state: confirmed
```

### R2

```product-relationship
type: capabilities
target: CAP-020
review:
  state: confirmed
```

### R3

```product-relationship
type: capabilities
target: CAP-030
review:
  state: confirmed
```

### R4

```product-relationship
type: capabilities
target: CAP-040
review:
  state: confirmed
```

### R5

```product-relationship
type: capabilities
target: CAP-050
review:
  state: confirmed
```

### R6

```product-relationship
type: capabilities
target: CAP-070
review:
  state: confirmed
```
