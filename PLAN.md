# Implementation Plan

Updated: 2026-09-01

## Current state

Product Modeler is in discovery and format prototyping. The repository currently contains:

- product scope, domain vocabulary, analysis guidance, and accepted architectural decisions;
- a fully migrated D+ dogfood Product Model under `model/`;
- the accepted D+ Markdown-first Claim profile in `format/DPLUS.md`;
- a Python parser, repository loader, indexer, validator, and graph-projection CLI under `reference_parser/`;
- preserved syntax experiments under `format/experiments/claim-syntax/` as historical design evidence.

The deterministic repository substrate is complete. On the dogfood model it reports:

- 34 discovered files: 30 D+ entities, one product manifest, and three support files;
- 31 unique entities and 114 Claims;
- 255 resolved graph edges;
- one Core Capability, no hierarchy or dependency cycles, and no diagnostics;
- 101 passing tests.

`product-model-parse inspect` exposes repository inventory, `validate` combines repository and graph validation, and `graph` emits the stable renderer-independent JSON projection.

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

See `CONTEXT.md`, `docs/product-brief.md`, and `docs/adr/` for authoritative detail. Confirmed Product Model Claims describe intended product behavior, not current implementation completeness.

## Next milestone: read-only explorer

Build the first user-facing view on top of the existing graph JSON projection. Do not add writes, chat, or AI analysis in this milestone.

### Scope

1. Render the Capability hierarchy rooted at `CAP-001`.
2. Expose cross-tree dependency links without confusing them with primary parentage.
3. Let the user inspect an entity's title, type, review summary, source path, Claims, relationships, and diagnostics.
4. Preserve partial-invalid behavior: usable graph content remains visible alongside diagnostics.
5. Keep all UI state derived and disposable; Product Model files remain authoritative.
6. Keep the viewer independent of the eventual mutation and conversation architecture.

### Design work required before implementation

- choose the application stack and graph/tree rendering approach;
- define the boundary between the Python projection CLI and the viewer;
- decide whether the first slice reads saved JSON or invokes the projection locally;
- define navigation and selection behavior for hierarchy edges versus dependency edges;
- define a minimal visual treatment for review states and unresolved references.

Do not add renderer-specific coordinates, colors, icons, or layout fields to graph schema `0.1`.

### Acceptance criteria

1. The viewer renders all eight Capabilities in their validated hierarchy.
2. Primary parent edges and cross-tree dependencies are visually distinguishable.
3. Selecting a node exposes its source location and Claim review summary.
4. Missing or invalid references can be shown from a partial projection without crashing.
5. The viewer does not mutate Product Model files.
6. Existing parser and repository tests continue to pass.
7. The graph projection remains deterministic and renderer-independent.

## Completed foundation

The following work is complete and should not be reimplemented unless its contract changes:

- strict D+ document parsing and content-digest validation;
- recursive repository discovery and file classification;
- manifest, D+, legacy, invalid, unsupported, and support-file handling;
- entity and Claim identity indexing without duplicate winner selection;
- cross-file reference extraction and resolution;
- Capability root, parent, connectivity, and cycle validation;
- dependency-cycle diagnostics;
- deterministic partial graph projection and JSON serialization;
- full dogfood migration from legacy entities to D+;
- clean-environment package installation and CLI execution.

Historical implementation specifications and pre-migration measurements remain available in Git history. The active plan intentionally does not duplicate them.

## Explicitly deferred

- editing Product Model files;
- Mutation Transaction application, staging, history, or Undo;
- adjacent clarification chat;
- LLM integration and question prioritization;
- prose-spec analysis;
- source-code or runtime prototype analysis;
- collaboration, estimates, scheduling, or implementation-task management.

## Work after the explorer

1. Add validated file-backed edits and Mutation Transactions.
2. Add adjacent clarification chat.
3. Implement prose-spec analysis.
4. Implement source-code prototype analysis.
5. Add optional runtime/browser evidence collection.
6. Test and refine the external coding-agent handoff.

## Open design questions

- `Q-004`: What is the minimum useful external-agent handoff contract?
- `Q-005`: How should Mutation Transaction history be stored and retained?

Neither blocks the read-only explorer.

## Resume checklist

Read:

1. `README.md`
2. `PLAN.md`
3. `CONTEXT.md`
4. `docs/product-brief.md`
5. `docs/analysis-method.md`
6. `docs/golden-path.md`
7. `format/DPLUS.md`
8. `reference_parser/README.md`
9. `docs/adr/0003` through `0006`

Then run:

```bash
git status --short
git log --oneline -8
PYTHONPATH=reference_parser python3 -m unittest discover -s reference_parser/tests -q
PYTHONPATH=reference_parser python3 -m product_model_parser inspect model/
PYTHONPATH=reference_parser python3 -m product_model_parser validate model/
PYTHONPATH=reference_parser python3 -m product_model_parser graph model/
```
