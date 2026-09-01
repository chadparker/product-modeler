# Product Model Format 0.1

This directory documents the experimental file format dogfooded in [`../model/`](../model/).

## Current authority

[`DPLUS.md`](DPLUS.md) is the normative profile for claim-bearing Product Model entities. The files under [`experiments/claim-syntax/`](experiments/claim-syntax/) are historical design evidence, not active alternatives or current syntax documentation.

The dogfood repository currently uses:

- one YAML product manifest, `model/product.yaml`;
- 30 D+ Markdown entity documents;
- three intentional Markdown support files.

No legacy entity documents remain in `model/`. The reference implementation in [`../reference_parser/`](../reference_parser/) defines repository classification, validation, and graph-projection behavior.

## Goals

- readable by humans and coding agents;
- representable as ordinary text files;
- stable entity identity across renames and moves;
- explicit hierarchy and dependency relationships;
- traceable Claims and uncertainty;
- extensible with established specialized formats;
- indexable as a graph without making the index authoritative.

## Entity documents

A claim-bearing entity is a D+ Markdown document with strict YAML frontmatter, one canonical H1 title, ordinary Markdown Claims, and structured relationship fences:

````markdown
---
formatVersion: "0.1"
id: CAP-030
type: capability
parent: CAP-001
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Resolve consequential uncertainty

## Claims

### C1

Questions are prioritized by expected downstream impact.

## Relationships

### R1

```product-relationship
type: requires
target: SUB-020
```
````

The globally stable Claim address is `CAP-030#C1`; the relationship address is `CAP-030#R1`. See [`DPLUS.md`](DPLUS.md) for the complete grammar, inheritance rules, and confirmation-digest algorithm.

## Initial entity types

- `product`
- `observation`
- `candidate-behavior`
- `capability`
- `journey`
- `interface`
- `domain-concept`
- `subsystem`
- `constraint`
- `question`
- `decision`
- `source`

The product manifest is YAML. Claim-bearing instances of the other types use D+.

## Separate state dimensions

Source reconstruction and target intent use separate concepts rather than one overloaded status.

### Observation Evidence Certainty

- `direct`
- `inferred`
- `contradicted`
- `unknown`

### Candidate Target Disposition

- `preserve`
- `modify`
- `exclude`
- `undecided`

### Intended-entity and Claim Review State

- `provisional`
- `confirmed`
- `questioned`
- `proposed`

A preselected Candidate Behavior may remain provisional until the user acts. The future import workflow must retain whether a disposition came from an import default or an explicit user choice.

D+ currently preserves an optional entity-level `status` field while Claims and relationships use `review.state`. Entity status is not an implementation-progress indicator, and confirmed Product Model intent does not imply that the feature has been built.

## Import strategies

The intended prototype-import workflow supports three initialization strategies:

- `prototype-as-starting-point` — Candidate Behaviors begin selected for preservation;
- `empty-target` — Candidate Behaviors begin excluded from the target;
- `review-individually` — Candidate Behaviors begin undecided.

These strategies are product design, not functionality in the current parser and graph implementation.

## Provenance and confirmation

Entities provide Provenance Defaults. Consequential Claims and relationships receive stable local IDs and override defaults only when their evidence or review metadata differs.

A statement should receive a Claim ID when it can be reviewed, contradicted, changed, sourced, implemented, or depended upon separately. Ordinary explanatory Context does not require Claim metadata.

Confirmed Claims carry a digest of normalized normative Markdown. Editing the content without reconfirming it produces a stale-confirmation validation error. Relationships may be confirmed without a content digest because their normative content is structured metadata.

## Relationships

D+ accepts string relationship types and entity-ID targets. The current Product Model uses relationship names including `supportedBy`, `requires`, `resolvedBy`, `capabilities`, `appliesTo`, and `related`.

Capability primary hierarchy is authoritative through the `parent` frontmatter field. Other relationships may express additional semantics but do not replace the parent index. The validator checks target syntax, existence, ambiguity, availability, and selected target-type constraints; it does not yet enforce a closed vocabulary of relationship types.

## Mutation transactions

Mutation Transactions, modes, staging, and Undo are accepted product design described in the Product Model and ADRs. They are not implemented by the current read-only parser, validator, or graph CLI.

The future design requires every AI-generated model change to be atomic and validated, with Balanced as the default Mutation Mode. The durable representation and retention policy for transaction history remains unresolved.

## Rules

1. IDs are stable and never derived from filenames.
2. A Capability has at most one primary parent.
3. Dependency relationships may cross the primary hierarchy.
4. Source Observations do not become intended behavior merely because they were detected.
5. Candidate Behaviors group related Observations for target selection.
6. Selecting a Candidate changes target intent; it does not change the certainty of its underlying Observations.
7. Source evidence does not become a Constraint without confirmation.
8. Filenames are descriptive conveniences.
9. Relative links may aid human reading; IDs remain authoritative for relationships.
10. Derived indexes must be safely rebuildable from model files.
11. Entity Provenance Defaults are inherited by Claims unless explicitly overridden.
12. Consequential Claims and relationships use stable local IDs addressable through their containing entity.

## Specialized artifacts

A model may embed or reference established formats where appropriate, including OpenAPI documents, Gherkin scenarios, design-token files, screenshots, and architecture diagrams. These supplement rather than replace the Product Model.

## Known unresolved issues

- exact representation of Candidate Behavior modifications;
- durable Mutation Transaction history and retention;
- deletion and rejection history;
- schema migration;
- whether relationship types should use a closed or extensible vocabulary;
- richer relationship-level review and provenance conventions;
- source-location stability across repository changes;
- model slicing for coding-agent context windows.
