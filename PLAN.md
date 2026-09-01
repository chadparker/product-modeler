# Implementation Plan

Updated: 2026-09-01

## Current state

Product Modeler is in discovery and format-prototyping. The repository contains:

- a product brief, domain glossary, analysis method, and golden-path scenario;
- a fully migrated D+ dogfood Product Model under `model/`;
- accepted architectural decisions under `docs/adr/`;
- the accepted D+ Markdown-first Claim profile in `format/DPLUS.md`;
- a Python D+ reference parser, repository indexer, validator and graph CLI, and 101 tests under `reference_parser/`;
- preserved syntax experiments and blind-review results under `format/experiments/claim-syntax/`.

The repository layer now discovers and classifies files, constructs deterministic entity, Claim, and reference indexes, rejects ambiguous duplicate identities, resolves D+ and legacy cross-file references, validates the product root and Capability hierarchy, detects structural and dependency cycles, and emits a stable graph JSON projection with partial-invalid behavior and source diagnostics. `product-model-parse inspect` exposes repository inventory; `validate` combines validation diagnostics; `graph` emits renderer-independent nodes, edges, and diagnostics.

## Accepted foundation

1. The product analyzes prose specifications and existing web-application prototypes.
2. It creates an implementation-independent, file-based Product Model.
3. It does not generate replacement applications.
4. The primary visualization is a Capability hierarchy with cross-tree dependencies.
5. Source behavior is represented as Observations grouped into selectable Candidate Behaviors.
6. Prototype imports support prototype-as-starting-point, empty-target, and review-individually strategies.
7. AI changes are atomic Mutation Transactions; Balanced is the default Mutation Mode.
8. Entities provide Provenance Defaults; consequential Claims use stable local IDs.
9. Claim-bearing entities use D+ Markdown with adjacent fenced YAML metadata.
10. Confirmed Claims carry content digests and become stale when their normative Markdown changes.

See `CONTEXT.md`, `docs/product-brief.md`, and `docs/adr/` for the authoritative detail.

## Next milestone: repository loader, index, and validator

Build the deterministic substrate that loads an entire Product Model directory and produces a validated graph. Do this before UI, chat, or AI analysis work.

### Milestone progress

Completed:

- deterministic recursive discovery, excluding hidden paths;
- UTF-8 and strict-YAML loading;
- classification of D+, manifest, legacy, support, unsupported, and invalid files;
- preservation of file and line diagnostics;
- deterministic JSON serialization;
- `product-model-parse inspect model/ [--json]`;
- dogfood classification: 1 manifest, 30 legacy entities, and 3 support files;
- immutable entity and Claim declaration records with source locations;
- deterministic declaration buckets and unambiguous identity lookups;
- duplicate entity and cross-document Claim diagnostics without choosing a winner;
- indexing of recoverable identities from invalid and unsupported files;
- `product-model-parse validate model/ [--json]`;
- dogfood indexing: 31 unique entity declarations, zero D+ Claims before migration, and no duplicate errors;
- D+ relationship-target and effective Claim/relationship provenance resolution;
- legacy parent, relation, provenance, source, resolution, related, applicability, and capability reference extraction;
- deterministic incoming and outgoing reference indexes;
- resolved Capability parent and children indexes;
- missing, ambiguous, unavailable, malformed, and wrong-type reference diagnostics;
- dogfood reference resolution: 79 resolved references, 7 Capability parent links, and no errors;
- exact product-manifest and Core Capability validation;
- deterministic Capability parent-cycle and disconnected-branch errors;
- deterministic dependency-cycle warnings, including self-cycles and multi-cycle components;
- iterative graph traversal that handles deep acyclic models without recursion failures;
- dogfood graph validation: one Core Capability, no hierarchy cycles, and no dependency cycles;
- immutable graph node, edge, and projection records plus a pure projection builder;
- schema-versioned, deterministic, JSON-safe graph output with partial-invalid semantics;
- renderer-independent projection of unambiguous entities and every syntactically valid reference;
- deterministic collision-free projection edge IDs and combined diagnostics;
- `product-model-parse graph model/ [--json]` with error/warning exit semantics;
- dogfood projection after full migration: product `PROD-001`, Core Capability `CAP-001`, 31 nodes, 255 resolved edges, 114 Claims, and no diagnostics;
- all 30 claim-bearing dogfood entities migrated to D+ while preserving the manifest, three support files, IDs, hierarchy, and legacy relationship semantics;
- 170 inherited provenance edges to `SRC-001`, valid confirmed Claim digests, and proposed/provisional/questioned states for unresolved or unconfirmed material.

Next implementation task: build the first read-only Capability hierarchy and dependency viewer from the stable graph JSON projection.

### Completed task specification: stable graph JSON projection

Implement this bounded slice after validation and before any UI work.

#### Projection API

Add immutable projection records and a pure builder, with names along these lines:

- `GraphNode`;
- `GraphEdge`;
- `GraphProjection`;
- `build_graph_projection(repository, index, graph_validation)`.

The projection is derived, disposable state. Source files remain authoritative. The builder must not read files again or mutate repository/index objects.

#### Top-level contract

Use an explicit projection schema version independent of D+ document versions:

```json
{
  "schemaVersion": "0.1",
  "product": "PROD-001",
  "coreCapability": "CAP-001",
  "valid": true,
  "nodes": [],
  "edges": [],
  "diagnostics": []
}
```

`product` and `coreCapability` may be `null` in a partial invalid projection. `valid` is false when any combined repository, index, or graph diagnostic is an error; warnings alone do not invalidate the projection.

#### Nodes

Create one node for each unambiguous entity declaration. Do not choose a winner for duplicate IDs. Each node should expose:

- `id` and `type`;
- canonical title, when available;
- source `path` and ID `line`;
- source file `kind` (`manifest`, `legacy`, `dplus`, `invalid`, or `unsupported`);
- whether the declaration is usable as a resolved target;
- entity status/review state when present;
- Claim and relationship counts;
- a deterministic Claim review-state summary for D+ documents;
- Capability parent ID when a valid parent edge exists.

Support files do not become graph nodes. Unique invalid or unsupported declarations may remain visible as unusable nodes so diagnostics and unavailable references have inspectable source context.

#### Edges

Project every syntactically valid indexed reference as an edge, including unresolved references. Each edge should expose:

- a deterministic projection-local `id`;
- semantic `kind` (`core-capability`, `parent`, `relationship`, `provenance`, or `source`);
- relationship type when applicable, such as `requires` or `resolvedBy`;
- source address and source entity ID;
- target entity ID;
- resolution (`resolved`, `missing`, `ambiguous`, or `unavailable`);
- source `path` and `line`.

Retain reference direction: for example, a Capability parent edge goes from the child Capability to its parent, and provenance goes from the entity/Claim/relationship to its evidence target. Malformed references without a syntactically valid target remain diagnostics rather than fabricated edges.

D+ relationship edges should use the relationship address as the basis of their edge identity. Generated identities for legacy, parent, source, and provenance edges must be deterministic and collision-free within one projection; they are projection identifiers, not new authoritative model IDs.

#### Diagnostics and partial output

Combine and deterministically sort:

- repository/classification diagnostics;
- D+ document diagnostics;
- identity and reference diagnostics;
- graph-validation diagnostics.

Always produce the best partial projection possible. Missing targets may be named by edges without corresponding nodes. Ambiguous entity IDs must remain omitted from the node map rather than being silently resolved. Invalid or unavailable content must remain visible through node/edge status and diagnostics.

#### Ordering and compatibility

- Sort nodes by entity ID.
- Sort edges by kind, relationship type, source, target, path, line, and generated ID.
- Sort diagnostics by path, line, code, and address.
- Serialize only JSON-native values; do not leak `Path`, Enum, dataclass, or parser objects.
- Keep the contract independent of Cytoscape, D3, React Flow, or any other rendering library.
- Treat field removal or semantic reinterpretation as a future schema-version change.

#### CLI

Add:

```bash
product-model-parse graph model/ --json
```

`--json` emits the complete projection. A non-JSON invocation may print a concise node/edge/diagnostic summary, but must not become an alternate authoritative format. Exit nonzero when the combined projection contains errors; dependency-cycle warnings alone retain a zero exit status.

#### Required tests

Add tests for:

1. mixed manifest, legacy, and D+ entities becoming nodes;
2. node title, source, kind, usability, status, counts, review summary, and parent fields;
3. core, parent, D+ relationship, legacy relationship, provenance, and source edges;
4. missing, ambiguous, and unavailable references retained as edges with resolution status;
5. duplicate entity IDs omitted rather than silently selected;
6. malformed references remaining diagnostics without fabricated edges;
7. deterministic, JSON-safe node, edge, and diagnostic ordering;
8. partial graph output and nonzero CLI exit when errors exist;
9. warning-only graph output and zero CLI exit;
10. pre-migration dogfood output containing 31 nodes, 79 edges, product `PROD-001`, Core Capability `CAP-001`, and no errors;
11. installation and `graph` execution in a clean virtual environment.

All existing 101 tests must continue to pass.

#### Explicitly deferred

Do not yet:

- render a graph or Capability tree;
- add UI-specific coordinates, colors, icons, or layout state;
- migrate the dogfood model to D+;
- add editing, chat, or Mutation Transactions.

The representative D+ dogfood vertical slice described below is now complete. The remaining migration should continue before building the read-only explorer UI.

### Completed task specification: identity indexing

This bounded slice was completed before cross-file reference resolution.

#### Data model

Add immutable declaration records with source locations:

- `EntityDeclaration`: entity ID, entity type, repository-relative path, ID line, file kind, and originating `RepositoryFile`;
- `ClaimDeclaration`: full address, entity ID, local Claim ID, repository-relative path, heading line, and originating Claim;
- `RepositoryIndex`: all declaration buckets plus unambiguous lookup maps.

The index should expose at least:

- entity ID → ordered tuple of every declaration;
- Claim address → ordered tuple of every declaration;
- repository-relative file path → entity declaration, when present;
- entity ID → declaration only when exactly one exists;
- Claim address → declaration only when exactly one exists.

Indexes are derived, disposable state. Do not write an index file or make it authoritative.

#### What counts as a declaration

- Include valid D+ documents, legacy entities, and the product manifest.
- Include invalid or unsupported files when classification recovered a syntactically valid entity ID; otherwise a conflicting declaration could be hidden.
- Index Claims only from D+ documents that parsed far enough to produce a `Document`.
- Do not index support files.

Add an explicit entity-ID source line to `RepositoryFile`; do not infer line numbers again during indexing.

#### Duplicate semantics

- Never choose a winner among duplicate declarations.
- Preserve all declarations in deterministic path/line order.
- Emit `entity.duplicate` on every declaration participating in an entity-ID collision.
- Emit `claim.duplicate` on every declaration participating in a Claim-address collision.
- Each diagnostic should identify the duplicated ID/address and list the other conflicting source locations.
- Unambiguous lookup maps must omit collided identities.
- Existing document-local duplicate checks remain in place; repository checks cover collisions across documents.

#### Validation CLI for this slice

Add:

```bash
product-model-parse validate model/
product-model-parse validate model/ --json
```

For now, `validate` should combine:

- discovery and classification diagnostics;
- D+ document diagnostics;
- entity duplicate diagnostics;
- Claim-address duplicate diagnostics.

It should exit nonzero when any error is present. Legacy migration warnings alone should not cause a nonzero exit. Keep `inspect` focused on classification and inventory.

#### Required tests

Add tests for:

1. a manifest, legacy entity, and D+ entity indexed together;
2. duplicate legacy entity IDs;
3. duplicate D+ entity IDs;
4. a collision between a legacy and D+ entity;
5. a duplicate involving an invalid or unsupported file with a recoverable ID;
6. duplicate Claim addresses caused by duplicate entity documents;
7. deterministic declaration and diagnostic ordering;
8. omission of collided identities from unambiguous lookups;
9. `validate` text and JSON output plus exit status;
10. the dogfood repository producing 31 unique entity declarations, zero indexed Claims before migration, and no duplicate errors.

All existing parser and repository tests must continue to pass.

#### Deferred beyond identity indexing

The following were deferred from the identity-indexing change and are now complete: cross-file target resolution, parent/provenance/source resolution, graph validation, and stable graph JSON projection.

### Proposed Python modules

```text
reference_parser/product_model_parser/
├── parser.py          # Existing single-document D+ parser
├── repository.py      # Discovery, loading, indexing, graph construction
├── diagnostics.py     # Optional extraction if diagnostics become unwieldy
└── __main__.py        # Extend CLI with repository commands
```

Do not split files merely to match this sketch; extract modules only when it improves clarity.

### CLI target

```bash
product-model-parse validate model/
product-model-parse inspect model/
product-model-parse graph model/ --json
```

The existing single-file invocation may remain supported or become an explicit `parse` subcommand with a compatibility path.

### Repository loading

1. Recursively discover supported files under a model directory.
2. Classify files as:
   - D+ Claim documents;
   - product manifests such as `product.yaml`;
   - legacy Markdown entities lacking `formatVersion`;
   - non-model support files such as appearance documentation.
3. Parse D+ documents with the existing reference parser.
4. Read enough metadata from legacy documents to report and incrementally migrate them; do not silently treat them as valid D+.
5. Preserve source file and line information for every indexed entity, Claim, relationship, and diagnostic.

### Indexes

Construct in-memory indexes for:

- entity ID → entity document;
- Claim address (`ENTITY-ID#LOCAL-ID`) → Claim;
- relationship source and target;
- Capability parent and children;
- incoming and outgoing dependencies;
- source/provenance references;
- file → contained entity.

Derived indexes are disposable and rebuildable. Model files remain authoritative.

### Repository validation

Report at least:

- duplicate entity IDs;
- duplicate Claim addresses;
- missing relationship targets;
- malformed or missing Capability parents;
- multiple or missing Core Capabilities where applicable;
- Capability hierarchy cycles as errors;
- dependency cycles as visible diagnostics, initially warnings rather than automatic errors;
- references to missing Sources, Decisions, Questions, or other entities;
- D+ stale confirmations;
- legacy files requiring migration;
- unsupported format versions.

Diagnostics need stable codes, severity, file, line, entity/Claim address, and a human-readable explanation.

### Graph output

Define a stable JSON projection suitable for the future UI:

```json
{
  "product": "PROD-001",
  "nodes": [],
  "edges": [],
  "diagnostics": []
}
```

Nodes should expose identity, type, title, review summary, source file, and relevant parent information. Edges should expose relationship identity, type, source, target, and provenance/review summary. Keep the projection independent of a specific graph-rendering library.

## Dogfood migration

After the repository loader can report mixed-format content, migrate one representative vertical slice to D+:

- `CAP-001` — Core Capability;
- `CAP-020` — infer product intent and behavior;
- `CAP-030` — resolve consequential uncertainty;
- `SUB-020` — AI analysis and question prioritization;
- `SUB-030` — evidence and provenance;
- `SUB-040` — clarification conversation and structured mutations;
- `JRN-001` — recover and clarify a product from source code;
- `UI-001` — product modeling workspace.

Use the migration to test:

- Claim granularity;
- relationships versus ordinary frontmatter fields;
- inherited provenance;
- mixed review states;
- cross-file reference resolution;
- graph projection readability.

The representative slice validated the conventions, and the remaining 22 legacy entities were then migrated. The dogfood repository is now fully D+ except for its YAML manifest and intentional support files.

## Acceptance criteria for the milestone

1. Running repository validation on `model/` completes without crashing.
2. Every model file is classified as valid D+, valid manifest, intentional support file, or legacy.
3. Duplicate and missing references produce deterministic diagnostics.
4. Parent hierarchy cycles are detected.
5. The migrated vertical slice parses and resolves across files.
6. `graph --json` emits deterministic output usable by a future UI.
7. Tests cover discovery, mixed formats, duplicate IDs, missing targets, cycles, stale Claims, and deterministic graph output.
8. Existing D+ document tests continue to pass.
9. The complete parser and repository suite passes.
10. The CLI installs and runs in a clean virtual environment.

## Explicit non-goals for this milestone

- source-code prototype analysis;
- LLM integration;
- chat;
- mutation application or Undo;
- browser/runtime inspection;
- visual graph rendering;
- collaboration, planning, estimates, or task management.

## Work after this milestone

1. Build a read-only Capability tree and dependency viewer from graph JSON.
2. Add entity and Claim inspection.
3. Add file-backed edits and Mutation Transactions.
4. Add adjacent clarification chat.
5. Implement prose-spec analysis.
6. Implement source-code prototype analysis.
7. Test external coding-agent handoff.

## Open design questions

- `Q-004`: What is the minimum useful external-agent handoff contract?
- `Q-005`: How should Mutation Transaction history be stored and retained?

Neither blocks the repository loader.

## Resume checklist

A new or compacted conversation should begin by reading:

1. `README.md`
2. `PLAN.md`
3. `CONTEXT.md`
4. `docs/product-brief.md`
5. `docs/analysis-method.md`
6. `docs/golden-path.md`
7. `format/DPLUS.md`
8. `reference_parser/README.md`
9. the latest relevant ADRs, especially `0003` through `0006`

Then run:

```bash
git status --short
git log --oneline -8
PYTHONPATH=reference_parser python3 -m unittest discover -s reference_parser/tests -q
PYTHONPATH=reference_parser python3 -m product_model_parser inspect model/
PYTHONPATH=reference_parser python3 -m product_model_parser validate model/
PYTHONPATH=reference_parser python3 -m product_model_parser graph model/ --json
PYTHONPATH=reference_parser python3 -m product_model_parser \
  format/experiments/claim-syntax/variant-d-plus.md
```

The next implementation task is the first read-only explorer consuming the stable graph JSON: render the Capability hierarchy rooted at `CAP-001`, expose cross-tree dependency links, and keep the UI independent of authoritative model storage. Define the UI boundary and technology choice before implementation; editing, chat, and mutation application remain deferred.
