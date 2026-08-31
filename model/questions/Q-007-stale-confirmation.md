---
id: Q-007
type: question
title: How should confirmed Claims become stale after content changes?
status: resolved
resolvedBy: DEC-004
impact: high
related:
  - DEC-003
  - Q-006
  - SUB-030
  - SUB-060
---

# How should confirmed Claims become stale after content changes?

## Resolution

Confirmed Claims store a SHA-256 digest of normalized normative Claim Markdown. Validation reports stale confirmation when current content does not match the recorded digest. Confirmed state and content digests cannot be inherited from entity defaults.

See [`../decisions/DEC-004-adopt-d-plus.md`](../decisions/DEC-004-adopt-d-plus.md) and [`../../format/DPLUS.md`](../../format/DPLUS.md).
