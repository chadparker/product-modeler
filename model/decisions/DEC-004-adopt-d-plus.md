---
id: DEC-004
type: decision
title: Adopt D+ Markdown Claim documents
status: accepted
date: 2026-08-31
resolves:
  - Q-006
  - Q-007
related:
  - DEC-003
  - CAP-040
  - SUB-030
  - SUB-060
---

# Adopt D+ Markdown Claim documents

Claim-bearing Product Model entities use the D+ Markdown-first profile. Claims are ordinary Markdown under stable local-ID headings, with optional adjacent fenced YAML metadata. Entity metadata and Provenance Defaults remain in strict YAML frontmatter.

Confirmed Claims carry a SHA-256 digest of normalized normative Markdown. If the content changes without reconfirmation, validation reports a stale confirmation. Confirmation and its digest cannot be inherited from entity defaults.

A tested Python reference parser defines the executable behavior of format version `0.1` without constraining the eventual application language.

See [`../../docs/adr/0006-adopt-d-plus-claim-documents.md`](../../docs/adr/0006-adopt-d-plus-claim-documents.md) and [`../../format/DPLUS.md`](../../format/DPLUS.md).
