# ADR 0004: Use configurable atomic mutation policies

- Status: Accepted
- Date: 2026-08-29

## Context

Applying every AI-generated model change immediately maximizes conversational speed but risks silently changing confirmed intent. Requiring approval for every change maximizes control but introduces confirmation fatigue and disrupts exploration. A hybrid policy can balance these concerns, but only if its behavior is predictable.

Explicit structured user actions, such as checking a Candidate Behavior or manually renaming an entity, already express clear intent and should not require redundant confirmation.

## Decision

Every AI-generated model change is represented as an atomic, validated Mutation Transaction. A transaction records its trigger, rationale, operations, affected entities, and before-and-after values. If any operation fails validation, none of the transaction is applied. Applied transactions support Undo.

Each project offers three Mutation Modes:

- **Fast** applies every valid AI-generated transaction immediately.
- **Review Everything** stages every AI-generated transaction for explicit acceptance.
- **Balanced** applies changes to provisional material and explicit structured user actions immediately, while staging AI-generated changes to confirmed or foundational intent.

Balanced is the default.

Balanced behavior is governed by visible deterministic rules rather than an opaque AI risk score. Changes to the Product Frame, Core Capability, confirmed behavior, Constraints, major concept merges, destructive operations, and broad dependency cascades require approval. Evidence attachment, provisional analysis, Clarification Question creation, and direct structured user actions apply immediately.

Every applied transaction produces a visible change summary and Undo action. Every staged transaction exposes rationale and affected entities before acceptance.

## Consequences

- Early analysis remains fluid while confirmed intent receives stronger protection.
- The system needs a structured mutation protocol and atomic validation boundary.
- The UI must distinguish applied and staged transactions clearly.
- Undo is a core capability, not optional polish.
- Rules determining protected changes must be documented and inspectable.
- A change may transition from immediate to staged as an entity moves from provisional to confirmed.
- The durable representation and retention policy for transaction history remains to be decided.
