# D+ Reference Parser

A small Python reference implementation of [`../format/DPLUS.md`](../format/DPLUS.md).

It intentionally uses a strict line-oriented Markdown profile rather than attempting to interpret arbitrary Markdown structure.

## Install

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e ./reference_parser
```

PyYAML 6 is the only runtime dependency.

## Use

```sh
product-model-parse format/experiments/claim-syntax/variant-d-plus.md
product-model-parse --json format/experiments/claim-syntax/variant-d-plus.md
product-model-parse --digests format/experiments/claim-syntax/variant-d-plus.md
product-model-parse inspect model/
product-model-parse inspect model/ --json
product-model-parse validate model/
product-model-parse validate model/ --json
product-model-parse graph model/
product-model-parse graph model/ --json
```

The command exits nonzero for structural parse failures or validation errors.

## Test

```sh
PYTHONPATH=reference_parser python3 -m unittest discover -s reference_parser/tests -v
```

## Scope

The parser validates individual D+ documents, discovers and classifies Product Model repositories, and builds deterministic entity, Claim, and cross-file reference indexes. Repository validation reports file/document errors, duplicate identities, missing or ambiguous targets, malformed references, invalid Capability parents, hierarchy cycles, disconnected branches, and dependency-cycle warnings while preserving source locations. The graph command emits a schema-versioned, renderer-independent projection with deterministic nodes, edges, diagnostics, and partial-invalid output.

The dogfood repository is fully migrated: its 30 claim-bearing entities are D+ documents, with 114 Claims and 255 resolved references. The graph projection contains 31 nodes, including the product manifest, and reports no diagnostics.
