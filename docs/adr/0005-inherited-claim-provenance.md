# ADR 0005: Use inherited claim-level provenance

- Status: Accepted
- Date: 2026-08-30

## Context

A Product Model entity often contains statements with different evidence, certainty, and review states. Entity-level provenance is readable but can misleadingly imply that every statement has the same support. Attaching metadata to every sentence is precise but produces excessive IDs, noise, and review burden.

Consequential relationships can also be observed, inferred, confirmed, or proposed independently of the entities they connect.

## Decision

Product Model entities provide Provenance Defaults inherited by their contained Claims. Consequential Claims receive stable local IDs and override inherited metadata only when necessary.

A Claim deserves independent identity when it can be confirmed or rejected separately, contradicted by evidence, changed independently, treated as an implementation requirement, linked to specific evidence, or depended upon by another behavior.

Claims are addressed using their entity ID and local ID, such as `CAP-030#C3`. Consequential relationships may likewise carry local IDs, such as `CAP-030#R1`.

Ordinary explanatory prose does not require Claim metadata. The UI supports entity-level summaries, bulk review, and individual Claim review.

## Consequences

- Provenance can be precise without attaching metadata to every sentence.
- Entities may contain mixed review states and summarize them in the UI.
- Claim IDs remain stable when wording changes.
- Agents and validators must understand inherited defaults.
- The format needs a readable convention connecting Claim metadata and Markdown text.
- Relationships may require metadata rather than remaining bare target IDs.
- At the time of this decision, existing version `0.1` dogfood entities continued using simplified entity-level fields pending a concrete Claim syntax. That migration was completed after ADR 0006 adopted D+.
