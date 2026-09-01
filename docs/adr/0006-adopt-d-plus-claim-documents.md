# ADR 0006: Adopt D+ Markdown Claim documents

- Status: Accepted
- Date: 2026-08-31

## Context

Inherited claim-level provenance requires a concrete file syntax that remains readable in Git, understandable to coding agents, deterministic to parse, and resistant to metadata drift.

Experiments compared YAML-first frontmatter, labelled Markdown blocks, Markdown with sidecars, and Markdown with adjacent fenced metadata. Two rounds of independent model review found a stable trade-off: YAML-first provides simpler parsing, while Markdown-first provides substantially better direct reading, multiline Claims, and review diffs. A second counterbalanced review split 2–2 between the improved finalists.

Confirmed Claims also need to become stale when their normative content changes.

## Decision

Adopt the D+ Markdown-first profile documented in [`../../format/DPLUS.md`](../../format/DPLUS.md).

- Entity metadata and Provenance Defaults live in strict YAML frontmatter.
- The canonical title is a single H1 and is not duplicated in frontmatter.
- Normative Claims use stable local-ID H3 headings and ordinary Markdown content.
- Optional Claim overrides use a final adjacent `product-claim` YAML fence.
- Relationships use `product-relationship` YAML fences without duplicated prose.
- Context is explicitly non-normative.
- A strict line-oriented profile defines heading, fence, inheritance, and normalization behavior.
- Confirmation is Claim-specific and stores a SHA-256 digest of normalized Claim content.
- Editing confirmed content without reconfirming it produces a stale-confirmation validation error.
- Confirmed review state and content digests cannot be inherited from entity defaults.

Maintain a small executable reference parser and validator with conformance tests. The initial implementation is Python with PyYAML as its only runtime dependency; this choice does not constrain the eventual application implementation language.

## Consequences

- Product Model files render and review as documents rather than configuration blobs.
- Parsing requires a documented Markdown profile plus strict embedded YAML handling.
- A validator is part of the format contract.
- Humans and agents can write multiline Claims, lists, links, and examples naturally.
- Claim confirmation remains tied to the exact content reviewed.
- Bulk confirmation must write a digest to each confirmed Claim rather than only changing an entity default.
- At acceptance, the existing dogfood files required incremental migration to D+; that migration is now complete.
- Cross-file reference existence remains a repository-level validation concern.
