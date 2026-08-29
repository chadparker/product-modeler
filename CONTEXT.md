# Domain Glossary

## Product Model

A durable, implementation-independent description of a software product's intended purpose, capabilities, behavior, experience, constraints, and unresolved questions.

## Product Evidence

Any source from which claims about a product can be derived, including prose, source code, tests, assets, screenshots, and runtime observations.

## Product Frame

The intended audience, problem, outcome, context, and scope boundaries of a product.

## Capability

A meaningful ability the product provides to a user or external actor.

## Core Capability

The primary capability that delivers the product's fundamental value.

## Supporting Capability

A capability that contributes to the Core Capability.

## Journey

A sequence of meaningful interactions through which an actor achieves an outcome.

## Interface

A screen, page, modal, panel, or other major interactive surface through which product behavior is exposed.

## Interface State

A meaningfully distinct condition of an Interface, such as empty, loading, populated, invalid, or failed.

## Domain Concept

A product concept with meaning to users or product behavior, independent of its implementation representation.

## Subsystem

A shared enabler required by one or more Capabilities.

## Constraint

A confirmed limitation or requirement that restricts acceptable implementations or behavior.

## Claim

A statement in the Product Model about the product.

## Provenance

The recorded origin, evidence relationship, and review information associated with a Claim.

## Observation

A structured conclusion about what a Source Prototype appears to do. An Observation remains separate from intended product behavior and carries an Evidence Certainty.

## Evidence Certainty

How strongly Product Evidence supports an Observation: direct, inferred, contradicted, or unknown.

## Candidate Behavior

A product-level behavior synthesized from one or more Observations and offered for inclusion in the intended Product Model.

## Target Disposition

The user's intended treatment of a Candidate Behavior: preserve, modify, exclude, or undecided.

## Import Strategy

The policy used to initialize Candidate Behavior dispositions: use the prototype as a starting point, start with an empty target, or review candidates individually.

## Review State

Whether an intended Product Model entity is provisional, confirmed, questioned, or proposed.

## Inference

A Claim reasoned from incomplete Product Evidence but not yet confirmed by the user.

## Confirmation

A Claim explicitly accepted by the user as intended product behavior.

## Proposal

A suggested product change that is not part of the currently confirmed Product Model.

## Mutation Transaction

An atomic, validated set of structured operations that changes the Product Model and records its trigger, rationale, affected entities, and before-and-after values.

## Mutation Mode

The project-level policy controlling when AI-generated Mutation Transactions are applied: Fast, Review Everything, or Balanced.

## Fast Mode

A Mutation Mode that applies valid AI-generated transactions immediately and relies on visible change summaries and Undo.

## Review Everything Mode

A Mutation Mode that stages every AI-generated transaction for explicit acceptance.

## Balanced Mode

The default Mutation Mode. It applies changes to provisional material and explicit structured user actions immediately, while requiring approval before AI-generated changes alter confirmed or foundational intent.

## Clarification Question

An unresolved question whose answer may change the Product Model.

## Preservation Policy

The required fidelity of an Interface or region: exact, structural, adaptive, inspirational, or unspecified.

## Source Prototype

An existing software product implementation analyzed as Product Evidence. It is not automatically authoritative about product intent.
