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
- `capability`
- `journey`
- `interface`
- `domain-concept`
- `subsystem`
- `constraint`
- `question`
- `decision`
- `source`

## Initial epistemic statuses

- `observed`
- `inferred`
- `confirmed`
- `proposed`
- `contradicted`
- `unknown`
- `rejected`

Entity status is a temporary simplification. Later versions may attach epistemic status to individual Claims because one entity can contain statements supported at different levels.

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
4. Source evidence does not become a Constraint without confirmation.
5. Filenames are descriptive conveniences.
6. Relative links should be used when a human-readable link is helpful; IDs remain authoritative for relationships.
7. Derived indexes must be safely rebuildable from model files.

## Specialized artifacts

A model may embed or reference established formats where appropriate, including OpenAPI documents, Gherkin scenarios, design-token files, screenshots, and architecture diagrams. These supplement rather than replace the Product Model.

## Known unresolved issues

- claim-level versus entity-level provenance;
- mutation and review protocol;
- deletion and rejection history;
- schema migration;
- relationship metadata;
- source-location stability across repository changes;
- model slicing for coding-agent context windows.
