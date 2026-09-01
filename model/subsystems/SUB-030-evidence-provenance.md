---
formatVersion: "0.1"
id: SUB-030
type: subsystem
status: confirmed
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Evidence and provenance

## Claims

### C1

The subsystem links consequential Claims to source locations and records Evidence Certainty for Observations and Review State for intended behavior.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:e3b5dd704d0143f39a3d491c85d4e2aa10ad5391c9298e7b532c8c8b66fbb466
```

### C2

Entities provide Provenance Defaults, while independently reviewable Claims and consequential relationships receive stable local IDs and override inherited metadata only where necessary.

```product-claim
review:
  state: confirmed
  contentDigest: sha256:e34ad726d993283131fef76ac4412a6089f078c716dd36451abb57ba78d04581
```
