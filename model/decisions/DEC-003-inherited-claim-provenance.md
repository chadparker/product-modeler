---
id: DEC-003
type: decision
title: Use inherited claim-level provenance
status: accepted
date: 2026-08-30
resolves:
  - Q-002
related:
  - SUB-030
  - CAP-040
---

# Use inherited claim-level provenance

Entities provide Provenance Defaults inherited by their contained Claims. Consequential Claims receive stable local IDs and override defaults only where necessary. Claims are addressed as an entity ID plus local ID, such as `CAP-030#C3`.

Consequential relationships may also receive local IDs. Ordinary explanatory prose does not require Claim metadata. The UI supports both bulk entity review and individual Claim review.

See [`../../docs/adr/0005-inherited-claim-provenance.md`](../../docs/adr/0005-inherited-claim-provenance.md).
