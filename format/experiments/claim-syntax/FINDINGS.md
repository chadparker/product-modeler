# Claim Syntax Evaluation Findings

Date: 2026-08-30

Three independent coding-oriented language models reviewed Variants A, B, and C against human readability, agent comprehension, parser reliability, diff quality, editing ergonomics, drift resistance, and provenance extensibility.

## Consensus

- Variant A was the strongest of the three as originally written because it has one authoritative structured representation and uses a standard YAML parser.
- Variant B was easiest to read but its em-dash headings, free-form labels, explicit `inherited` sentinels, and duplicated relationship text create a fragile custom grammar.
- Variant C preserves clean Markdown but introduces a cross-file join that humans and agents can easily leave inconsistent.
- No original variant adequately detects a confirmed Claim whose statement is later edited while its review metadata remains unchanged.

## Reviewer recommendations

Two reviewers independently recommended a constrained hybrid represented here as [`variant-d-fenced-metadata.md`](variant-d-fenced-metadata.md):

- entity identity and Provenance Defaults remain in frontmatter;
- each Claim uses an ID-only Markdown heading;
- the authoritative Claim content is ordinary Markdown beneath that heading;
- optional structured overrides use an adjacent fenced YAML block;
- relationships use fenced structured metadata without duplicating type or target in prose;
- absence of an override means inheritance.

One reviewer recommended a constrained Variant A instead, using ID-keyed YAML mappings, mandatory quoting or block scalars, and one authoritative title location. Its main argument was that frontmatter requires only a YAML parser, whereas Variant D still requires a small Markdown profile.

## Provisional ranking

1. Variant D — best balance if its Markdown profile is narrow and validated.
2. Variant A+ — safest fallback if parser simplicity is valued over rendered readability.
3. Variant B — readable but insufficiently deterministic as written.
4. Variant C — unacceptable without strict cross-file validation.

## Variant D parsing profile

A deterministic parser can require:

1. Entity metadata in YAML frontmatter.
2. Claim sections under `## Claims`.
3. Claim headings matching `### <local-id>` with no statement in the heading.
4. Authoritative Claim content consisting of Markdown beneath the heading, excluding the optional final `product-claim` fence.
5. Relationship sections under `## Relationships`.
6. Relationship headings matching `### <local-id>`.
7. Exactly one `product-relationship` YAML fence per relationship.
8. No stored `inherited` sentinel; absence means inheritance.
9. Unique local IDs within each entity.

## Newly exposed issue: stale confirmation

All variants allow this failure:

1. A Claim is confirmed.
2. Its statement is materially edited.
3. Its metadata still says confirmed.

A possible defense is to store a digest of the normalized Claim content when confirmation occurs. If the content later differs, validation marks the review stale until reconfirmed. This affects whether review state can safely be inherited at entity level and should be decided before finalizing Claim syntax.

## Current recommendation

Continue with Variant D as the leading candidate, but do not accept it as the durable syntax until stale-confirmation behavior and the exact normalized Claim-content boundary are resolved.
