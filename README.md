# Product Modeler

An AI-assisted environment for turning software-product evidence into a durable, implementation-independent Product Model.

The system accepts prose specifications and existing web-application source code, constructs a provisional structured model, and refines it through an evidence-backed clarification conversation. It does **not** build the resulting product; its file-based output is intended for humans and external coding agents.

## Repository layout

- [`PLAN.md`](PLAN.md) — current implementation plan and restart handoff
- [`CONTEXT.md`](CONTEXT.md) — canonical domain vocabulary
- [`docs/product-brief.md`](docs/product-brief.md) — product scope and principles
- [`docs/analysis-method.md`](docs/analysis-method.md) — reasoning hierarchy
- [`docs/golden-path.md`](docs/golden-path.md) — first end-to-end scenario
- [`docs/adr/`](docs/adr/) — durable architectural decisions
- [`model/`](model/) — dogfood Product Model for Product Modeler itself
- [`format/`](format/) — evolving format documentation and D+ profile
- [`reference_parser/`](reference_parser/) — executable D+ parser, validator, CLI, and conformance tests

## Status

Discovery and format prototyping. The dogfood model uses format version `0.1` and is expected to change without backward compatibility.
