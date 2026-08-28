# ADR 0002: Separate product intent from implementation evidence

- Status: Accepted
- Date: 2026-08-28

## Context

An existing prototype contains valuable evidence about behavior and appearance, but also contains accidents, abandoned experiments, technical compromises, and framework-specific structure. Treating every implementation detail as a requirement would make later implementations needlessly reproduce the old prototype.

## Decision

The Product Model primarily describes intended, user-observable product behavior independently of implementation.

Source code, tests, schemas, assets, and runtime observations are Product Evidence. Claims derived from them carry Provenance and an epistemic status such as observed, inferred, confirmed, proposed, contradicted, or unknown.

An implementation detail becomes a Constraint only when explicitly confirmed as something a future implementation must preserve.

## Consequences

- A future coding agent may choose a different architecture while preserving product intent.
- Reverse engineering requires judgment rather than mechanical transcription.
- The UI must expose evidence and uncertainty clearly.
- Clarification is required when observed behavior and intended behavior may differ.
- Source references must remain traceable even when they are not authoritative.
