---
id: Q-002
type: question
title: Should provenance attach to entities or individual claims?
status: unknown
impact: high
related:
  - SUB-030
  - CAP-040
---

# Should provenance attach to entities or individual claims?

Entity-level provenance is simpler but becomes misleading when one document mixes observed, inferred, and confirmed statements. Claim-level provenance is more precise but may make authoring and reading cumbersome.

The version `0.1` files temporarily use entity-level status and provenance while treating claim-level representation as unresolved.
