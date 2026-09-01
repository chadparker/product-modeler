---
formatVersion: "0.1"
id: SUB-050
type: subsystem
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# File persistence

## Claims

### C1

The subsystem reads and writes the authoritative Product Model directory while preserving stable IDs and producing understandable Git diffs.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:8871876081781d070732000fc24c22911e6abbf7d9b3437e3cea3df69596580f
```
