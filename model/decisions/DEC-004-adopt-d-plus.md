---
formatVersion: "0.1"
id: DEC-004
type: decision
status: accepted
date: 2026-08-31
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Adopt D+ Markdown Claim documents

## Context

See [`../../docs/adr/0006-adopt-d-plus-claim-documents.md`](../../docs/adr/0006-adopt-d-plus-claim-documents.md) and [`../../format/DPLUS.md`](../../format/DPLUS.md) for the authoritative rationale and syntax.

## Claims

### C1

Claim-bearing Product Model entities use the D+ Markdown-first profile.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:a3afc65673b768318c55b8c84fd3beebb1e91e50aaaa51670d0e5d30734fa012
```

### C2

Claims are ordinary Markdown under stable local-ID headings with optional adjacent fenced YAML metadata, while entity metadata and Provenance Defaults remain in strict YAML frontmatter.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:17d243b535111cdf6afb885e4f4ff5098d851bd34229a8aab2aeef4a112fbd96
```

### C3

Confirmed Claims carry a SHA-256 digest of normalized normative Markdown, and validation reports stale confirmation when the content changes without reconfirmation.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:5d02196ceb2a72cad23b90831d0a953e354e333455632662cc92600c8512d29f
```

### C4

Confirmation state and its content digest cannot be inherited from entity defaults.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:c57a026ad0c254a6dcf0860e50e476dea911a4866e9fd58c1a6e8e7bf3acbfb8
```

### C5

A tested Python reference parser defines the executable behavior of D+ format version `0.1` without constraining the eventual application language.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:e34ae9a7aa449bc46b3ed02fd854719f5eebd8e012ca50a071f37d9258fbd74d
```

## Relationships

### R1

```product-relationship
type: resolves
target: Q-006
review:
  state: confirmed
```

### R2

```product-relationship
type: resolves
target: Q-007
review:
  state: confirmed
```

### R3

```product-relationship
type: related
target: DEC-003
review:
  state: confirmed
```

### R4

```product-relationship
type: related
target: CAP-040
review:
  state: confirmed
```

### R5

```product-relationship
type: related
target: SUB-030
review:
  state: confirmed
```

### R6

```product-relationship
type: related
target: SUB-060
review:
  state: confirmed
```
