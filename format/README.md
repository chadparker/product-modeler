# Product Model Format 0.1

This directory documents the experimental file format dogfooded in [`../model/`](../model/).

## Goals

- readable by humans and coding agents;
- representable as ordinary text files;
- stable entity identity across renames and moves;
- explicit hierarchy and dependency relationships;
- traceable Claims and uncertainty;
- extensible with established specialized formats;
- indexable as a graph without making the index authoritative.

## Entity documents

Most entities are Markdown files with YAML frontmatter:

```markdown
---
id: CAP-002
type: capability
title: Analyze prose specifications
parent: CAP-001
relations:
  requires:
    - SUB-001
status: confirmed
provenance:
  - kind: confirmation
    source: SRC-001
---

# Analyze prose specifications

The system derives a provisional Product Model from prose or outline input.
```

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

## Separate state dimensions

Source reconstruction and target intent use separate fields rather than one overloaded status.

### Observation evidence certainty

- `direct`
- `inferred`
- `contradicted`
- `unknown`

### Candidate target disposition

- `preserve`
- `modify`
- `exclude`
- `undecided`

### Intended-entity review state

- `provisional`
- `confirmed`
- `questioned`
- `proposed`

A preselected candidate may remain provisional until the user acts. The format should retain whether a disposition came from an import default or an explicit user choice.

## Import strategies

Prototype import supports three initialization strategies:

- `prototype-as-starting-point` — candidate behaviors begin selected for preservation;
- `empty-target` — candidate behaviors begin excluded from the target;
- `review-individually` — candidate behaviors begin undecided.

The UI may expose these as Select All, Select None, and Review Individually. Raw Observations are grouped into product-level Candidate Behaviors before selection.

## Temporary legacy status values

The current dogfood files still use a simplified entity-level `status` field:

- `observed`
- `inferred`
- `confirmed`
- `proposed`
- `contradicted`
- `unknown`
- `rejected`

This field is transitional. Evidence Certainty, Target Disposition, and Review State must not be collapsed into one status in the durable schema.

## Inherited claim-level provenance

Entities provide Provenance Defaults. Consequential Claims receive stable local IDs and override defaults only when their evidence or review metadata differs.

```yaml
id: CAP-030
type: capability
title: Search collected sources

defaults:
  review: provisional
  basedOn:
    - OBS-020

claims:
  - id: C1
    statement: Users can search source titles.

  - id: C2
    statement: Users can search annotation text.
    review: confirmed
    basedOn:
      - SRC-003
```

The globally stable address for the second Claim is `CAP-030#C2`. Consequential relationships may similarly use local IDs such as `R1`, addressed as `CAP-030#R1`.

A statement should receive a Claim ID when it can be reviewed, contradicted, changed, sourced, implemented, or depended upon separately. Ordinary explanatory prose does not require Claim metadata.

The exact convention connecting frontmatter Claims to Markdown body text remains experimental.

## Mutation transactions

Every AI-generated model change is expressed as an atomic, validated Mutation Transaction. A transaction identifies:

- the triggering chat message, analysis event, or user action;
- the active Mutation Mode;
- its rationale;
- structured operations;
- affected entity IDs;
- before-and-after values;
- whether it was applied, staged, rejected, or undone.

Projects support:

- `fast` — immediately apply all valid AI-generated transactions;
- `review-everything` — stage all AI-generated transactions;
- `balanced` — immediately apply provisional and explicit structured user changes, but stage changes to confirmed or foundational intent.

Balanced is the default. Protected categories are deterministic and visible. Applied transactions support atomic Undo; failed validation writes nothing.

The durable file representation and retention policy for transaction history is not yet defined.

## Core relationships

- `supports`
- `requires`
- `appears-in`
- `participates-in`
- `transitions-to`
- `constrained-by`
- `evidenced-by`
- `contradicts`
- `alternative-to`

## Rules

1. IDs are stable and never derived from filenames.
2. A Capability has at most one primary parent.
3. Dependency relationships may cross the primary hierarchy.
4. Source Observations do not become intended behavior merely because they were detected.
5. Candidate Behaviors group related Observations for target selection.
6. Selecting a Candidate changes target intent; it does not change the certainty of its underlying Observations.
7. Source evidence does not become a Constraint without confirmation.
8. Filenames are descriptive conveniences.
9. Relative links should be used when a human-readable link is helpful; IDs remain authoritative for relationships.
10. Derived indexes must be safely rebuildable from model files.
11. Entity Provenance Defaults are inherited by Claims unless explicitly overridden.
12. Consequential Claims and relationships use stable local IDs addressable through their containing entity.

## Specialized artifacts

A model may embed or reference established formats where appropriate, including OpenAPI documents, Gherkin scenarios, design-token files, screenshots, and architecture diagrams. These supplement rather than replace the Product Model.

## Known unresolved issues

- exact representation of candidate-to-target modifications;
- concrete Markdown/YAML syntax for Claims without duplicated text;
- durable mutation-history representation and retention;
- deletion and rejection history;
- schema migration;
- relationship metadata;
- source-location stability across repository changes;
- model slicing for coding-agent context windows.
