---
id: Q-007
type: question
title: How should confirmed Claims become stale after content changes?
status: unknown
impact: high
related:
  - DEC-003
  - Q-006
  - SUB-030
  - SUB-060
---

# How should confirmed Claims become stale after content changes?

A Claim can be confirmed and later edited while its metadata still says confirmed. The model needs a deterministic way to detect that the reviewed content changed.

One option is to store a digest of normalized Claim content at confirmation time and mark review state stale when the current digest differs. This may limit whether confirmed review state can safely be inherited from an entity default.
