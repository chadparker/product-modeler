---
formatVersion: "0.1"
id: CAP-030
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

# Resolve consequential uncertainty

## Claims

### C1

The user and AI can refine the provisional Product Model through a conversation adjacent to the model.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:5820ff3661dc5f82a846da208ac3862a53a4020d9edfa69989881d9a6a8d671b
```

### C2

The system identifies ambiguity, prioritizes Clarification Questions by expected downstream impact, and translates answers into atomic validated Mutation Transactions.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:c513389adb92c4f91593ee718176e40ad4061ad146aee27085553af5a9a6fffa
```

### C3

Clarification Questions do not block creation of the first provisional Product Model.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f190bbd9fd0d98b64787aaae7533930e2064c6184d439f7a65d43516535d5e2d
```

### C4

Each project offers Fast, Review Everything, and Balanced Mutation Modes.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:8748a0604ef2f46b065aa796571ea5d5eb660f138364a44da34dc8ff61e4dea8
```

### C5

Balanced is the default Mutation Mode and requires approval before AI-generated changes alter confirmed or foundational intent.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:52cd2ec3d65e84dd4f9be1e1c7ac3db7ac039a55e5ef51e0726fcd47b6ba7294
```

### C6

Every applied Mutation Transaction is summarized and supports atomic Undo.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a37b08e984956fa67e0a54c88e1591b490c67938120371f0c2118f02af944fc7
```

### C7

Rejected Inferences remain traceable without cluttering the active Product Model.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:00f2f3c7b193e2501673db9d74b04acf340bf04958a0e5c070bd24adeab72c3f
```

## Relationships

### R1

```product-relationship
type: requires
target: CAP-020
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
target: SUB-040
review:
  state: confirmed
```
