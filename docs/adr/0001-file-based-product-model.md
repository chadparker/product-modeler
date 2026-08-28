# ADR 0001: Use a file-based Product Model

- Status: Accepted
- Date: 2026-08-28

## Context

The Product Model must be durable, inspectable, versionable, and usable by humans and coding agents without requiring Product Modeler to be running. A database would simplify graph queries, while a bespoke binary format could optimize storage, but either would weaken direct readability and portability.

## Decision

The authoritative Product Model will be stored as a directory of text files suitable for Git.

The initial format uses Markdown documents with YAML frontmatter for entities and relationships, plus YAML or JSON for compact manifests and machine-validation schemas. Stable IDs connect entities independently of filenames.

Applications may build database, search, or graph indexes as disposable caches derived from the files.

## Consequences

- Humans and agents can inspect and modify the model directly.
- Git provides history, diffs, branching, and transport.
- The format needs explicit validation and migration conventions.
- File changes from concurrent tools may require reconciliation.
- Graph queries may require a derived index.
- Format version `0.1` is experimental and not backward-compatible.
