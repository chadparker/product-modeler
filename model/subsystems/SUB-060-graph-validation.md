---
formatVersion: "0.1"
id: SUB-060
type: subsystem
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Graph indexing and model validation

## Claims

### C1

The subsystem builds disposable graph indexes from Product Model files and detects invalid references, duplicate IDs, broken hierarchy, unsupported relationships, and schema violations.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:f7bcdbb11b2954075eb35ccbcc249cb949a9655ff94b81633c27d587ab4a4048
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-050
review:
  state: confirmed
```
