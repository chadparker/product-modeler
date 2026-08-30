# Claim Syntax Experiment

This experiment represents the same Capability using three candidate syntaxes. Each variant must keep authoritative statement text in one place while supporting:

- entity Provenance Defaults;
- stable local Claim and relationship IDs;
- per-Claim overrides;
- readable Markdown;
- deterministic parsing;
- direct editing by humans and coding agents.

## Shared semantic content

Capability `CAP-030`, **Resolve consequential uncertainty**, contains four Claims:

- `C1` — Clarification Questions do not block creation of the first provisional model.
- `C2` — Questions are prioritized by expected downstream impact.
- `C3` — Balanced is the default Mutation Mode.
- `C4` — Every applied Mutation Transaction is summarized and supports atomic Undo.

It also requires `SUB-020` and `SUB-040` through relationships `R1` and `R2`.

## Variants

- [`variant-a-frontmatter.md`](variant-a-frontmatter.md) — statements and metadata live in YAML frontmatter.
- [`variant-b-markdown-blocks.md`](variant-b-markdown-blocks.md) — Claims are first-class Markdown sections with structured labels.
- [`variant-c/`](variant-c/) — readable Markdown statements and a separate YAML metadata sidecar.
- [`variant-d-fenced-metadata.md`](variant-d-fenced-metadata.md) — ID-only Markdown sections with adjacent fenced YAML overrides, added after independent review.

See [`FINDINGS.md`](FINDINGS.md) for the evaluation summary.

## Evaluation criteria

1. Human readability
2. Coding-agent readability
3. Parser reliability
4. Diff quality
5. Editing ergonomics
6. Resistance to text/metadata drift
7. Ability to add richer provenance later

No variant is accepted merely by appearing in this experiment.
