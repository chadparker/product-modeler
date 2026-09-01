---
formatVersion: "0.1"
id: Q-006
type: question
status: resolved
impact: medium
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# What concrete Markdown syntax should represent Claims?

## Context

Resolved by [`DEC-004`](../decisions/DEC-004-adopt-d-plus.md). The normative profile and parser are documented in [`../../format/DPLUS.md`](../../format/DPLUS.md) and [`../../reference_parser/`](../../reference_parser/).

## Claims

### C1

The model uses the D+ Markdown-first profile: entity metadata and defaults in YAML frontmatter, Claims as ordinary Markdown under stable local-ID headings, and optional structured overrides in adjacent `product-claim` fences.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a6cf9cbbb8e21bd2481fc331a84c16c4db1a0d95e8b96489cc22c51f6dd32aa9
```

### C2

Relationships use adjacent `product-relationship` fences.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:881487b5a2e85128b29e3743d698c4a5d536f70098118a78b0eaeab582b20173
```

## Relationships

### R1

```product-relationship
type: resolvedBy
target: DEC-004
review:
  state: confirmed
```

### R2

```product-relationship
type: related
target: DEC-003
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: CAP-040
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
