---
id: Q-006
type: question
title: What concrete Markdown syntax should represent Claims?
status: resolved
resolvedBy: DEC-004
impact: medium
related:
  - DEC-003
  - CAP-040
  - SUB-030
---

# What concrete Markdown syntax should represent Claims?

## Resolution

Adopt the D+ Markdown-first profile: entity metadata and defaults in YAML frontmatter, Claims as ordinary Markdown under stable local-ID headings, and optional structured overrides in adjacent `product-claim` fences. Relationships use `product-relationship` fences.

The normative profile and reference parser are documented in [`../../format/DPLUS.md`](../../format/DPLUS.md) and [`../../reference_parser/`](../../reference_parser/).

See [`../decisions/DEC-004-adopt-d-plus.md`](../decisions/DEC-004-adopt-d-plus.md).
