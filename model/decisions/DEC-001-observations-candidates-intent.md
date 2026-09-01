---
formatVersion: "0.1"
id: DEC-001
type: decision
status: accepted
date: 2026-08-29
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Separate observations, candidate behaviors, and intended product entities

## Context

See [`../../docs/adr/0003-observations-candidates-and-intent.md`](../../docs/adr/0003-observations-candidates-and-intent.md) for the architectural rationale.

## Claims

### C1

Source analysis records granular Observations and groups related Observations into Candidate Behaviors.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:ae30c912d46432074e088c9cccaf88caaff710f49e25e6c59fec1c735c268682
```

### C2

Candidate Behaviors are offered for inclusion in the intended Product Model with a Target Disposition of preserve, modify, exclude, or undecided.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:bd994f451301cf1c2f8b4d5faac1442840fd19101258af1cc55fc94303e84e90
```

### C3

Prototype import supports prototype-as-starting-point, empty-target, and review-individually Import Strategies.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:ccb6eb3f4162fead873f830043d3a20f5aa2cdc4cda1d5e5e9aa9f33971fac92
```

### C4

Selecting a Candidate Behavior determines target intent without changing Evidence Certainty.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:52455d58c7d4bfc821da34aee007b4941b3d5ec892cfd6fe1ec7e8a861e8213d
```

### C5

Prototype-as-starting-point is the default Import Strategy, and the user may apply all, none, branch-level, or individual Candidate Behavior choices.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:7d9dcc1592c86fc9b3b60bb56ef14a6127baf19a135a698a8abb19759200612a
```

## Relationships

### R1

```product-relationship
type: resolves
target: Q-003
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: CAP-020
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: CAP-030
review:
  state: confirmed
```

### R4

```product-relationship
type: related
target: SUB-030
review:
  state: confirmed
```
