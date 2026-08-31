# Implementation Plan

Updated: 2026-08-31

## Current state

Product Modeler is in discovery and format-prototyping. The repository contains:

- a product brief, domain glossary, analysis method, and golden-path scenario;
- a dogfood Product Model under `model/`;
- accepted architectural decisions under `docs/adr/`;
- the accepted D+ Markdown-first Claim profile in `format/DPLUS.md`;
- a Python D+ reference parser, repository file classifier, CLI, and 54 tests under `reference_parser/`;
- preserved syntax experiments and blind-review results under `format/experiments/claim-syntax/`.

The repository layer now discovers files recursively and classifies D+ documents, the product manifest, legacy entities, support files, unsupported versions, and invalid files. It preserves file/line diagnostics and exposes deterministic JSON through `product-model-parse inspect`. It does not yet construct cross-file indexes or resolve references.

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
- dogfood classification: 1 manifest, 30 legacy entities, and 3 support files.

Next implementation task: construct entity and Claim indexes and diagnose duplicate IDs. Reference resolution and graph construction follow.

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

Do not migrate every file until this slice validates cleanly and reads well without tooling.

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

1. Complete dogfood migration.
2. Build a read-only Capability tree and dependency viewer from graph JSON.
3. Add entity and Claim inspection.
4. Add file-backed edits and Mutation Transactions.
5. Add adjacent clarification chat.
6. Implement prose-spec analysis.
7. Implement source-code prototype analysis.
8. Test external coding-agent handoff.

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
PYTHONPATH=reference_parser python3 -m product_model_parser \
  format/experiments/claim-syntax/variant-d-plus.md
```

The next implementation task is entity and Claim indexing with deterministic duplicate-ID diagnostics.
