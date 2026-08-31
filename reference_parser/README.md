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
```

The command exits nonzero for structural parse failures or validation errors.

## Test

```sh
PYTHONPATH=reference_parser python3 -m unittest discover -s reference_parser/tests -v
```

## Scope

The parser currently validates document structure, strict YAML, IDs, provenance inheritance, relationship fields, review states, and Claim confirmation digests. Cross-file target and source resolution belongs to the future model-level validator.
