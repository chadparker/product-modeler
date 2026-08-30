---
id: Q-002
type: question
title: Should provenance attach to entities or individual claims?
status: resolved
resolvedBy: DEC-003
impact: high
related:
  - SUB-030
  - CAP-040
---

# Should provenance attach to entities or individual claims?

## Resolution

Entities provide Provenance Defaults inherited by their contained Claims. Consequential Claims and relationships receive stable local IDs and override defaults only where necessary. Ordinary explanatory prose remains unannotated.

A Claim is addressed using its entity ID and local ID, such as `CAP-030#C3`.

See [`../decisions/DEC-003-inherited-claim-provenance.md`](../decisions/DEC-003-inherited-claim-provenance.md).
