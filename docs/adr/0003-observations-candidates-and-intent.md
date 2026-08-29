# ADR 0003: Separate observations, candidate behaviors, and intended product entities

- Status: Accepted
- Date: 2026-08-29

## Context

A Source Prototype may contain behavior the user wants to preserve, modify, or remove. Source analysis also produces many low-level observations that are too granular for individual target-selection decisions. A single status field cannot accurately represent evidence certainty, target inclusion, and user review.

Two complete baseline and target Product Models would make comparison clear but duplicate most content and create synchronization ambiguity. A single combined model would be compact but conflate what exists with what is intended.

## Decision

Source analysis produces three distinct layers:

1. **Observations** record what the Source Prototype appears to do and carry Evidence Certainty.
2. **Candidate Behaviors** group related Observations into product-level choices.
3. **Intended Product Model entities** describe what an external coding agent should build and carry Review State.

Each Candidate Behavior has a Target Disposition of preserve, modify, exclude, or undecided. Selecting a candidate changes target intent; it does not confirm the accuracy of its underlying Observations.

Prototype import offers three initialization strategies:

- use the prototype as a starting point;
- start with an empty target;
- review candidates individually.

The first strategy is the default. The UI supports Select All, Select None, branch-level selection, and individual modification.

## Consequences

- The intended Product Model remains clean and implementation-independent.
- Existing behavior remains traceable even when deliberately excluded.
- Users can choose between reconstruction-first and blank-slate workflows.
- The analyzer must group raw Observations into coherent Candidate Behaviors.
- Evidence certainty, target disposition, and user review require separate fields.
- Modified candidates need explicit links between observed and intended behavior.
- The comparison UI can derive preserved, modified, excluded, introduced, and unresolved behavior without maintaining two complete Product Models.
