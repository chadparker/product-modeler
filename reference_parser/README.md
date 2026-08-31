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
```

The command exits nonzero for structural parse failures or validation errors.

## Test

```sh
PYTHONPATH=reference_parser python3 -m unittest discover -s reference_parser/tests -v
```

## Scope

The parser validates individual D+ documents and can discover and classify all files in a Product Model repository. Repository inspection distinguishes D+ documents, the product manifest, legacy entities, support files, unsupported versions, and invalid files. Cross-file indexing and reference resolution are the next layer.
