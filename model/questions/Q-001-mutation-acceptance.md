---
id: Q-001
type: question
title: Must AI mutations be accepted before writing files?
status: unknown
impact: high
related:
  - CAP-030
  - SUB-040
---

# Must AI mutations be accepted before writing files?

Possible policies:

1. Apply every mutation immediately and rely on Git/history for reversal.
2. Require explicit acceptance for every mutation.
3. Apply low-risk changes immediately while staging consequential changes.

This affects interaction speed, trust, review UI, and the mutation protocol.
