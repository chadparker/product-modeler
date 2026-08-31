# Product Brief

## Purpose

Product Modeler helps people understand and deliberately evolve software products before handing their definition to an implementation agent.

It converts incomplete product evidence into a structured Product Model, makes the model explorable as a capability hierarchy with dependency links, and uses conversation to resolve consequential uncertainty.

## Initial users

People who have either:

- a prose or outline specification for a software product, or
- an existing web-application prototype whose product intent needs to be recovered and refined.

## Core outcome

The user obtains a readable, evidence-backed, implementation-independent Product Model that can guide a new implementation by any coding agent.

## Initial scope

The first version:

- accepts prose specifications and local web-application source repositories;
- analyzes static source evidence;
- may optionally run a web prototype for richer behavioral and appearance evidence;
- records source behavior as Observations rather than treating it as intended behavior;
- groups related Observations into selectable Candidate Behaviors;
- lets the user initialize the intended model from all candidates, no candidates, or an individually reviewed selection;
- constructs a provisional model immediately when the prototype-as-starting-point strategy is selected;
- displays capabilities as a primary hierarchy with cross-tree dependencies;
- asks prioritized clarification questions through adjacent chat;
- expresses AI changes as atomic, validated Mutation Transactions;
- defaults to Balanced mutation handling while offering Fast and Review Everything modes;
- records observations, inferences, confirmations, proposals, and contradictions;
- attaches inherited provenance defaults to entities and precise metadata to consequential Claims;
- stores the authoritative model as text files suitable for Git;
- records optional appearance references with granular preservation policies.

## Explicit exclusions

The product does not:

- generate or build a replacement prototype;
- prescribe a particular coding agent;
- provide collaboration workflows;
- estimate work;
- schedule work;
- manage implementation tasks;
- track project delivery.

## Principles

1. **Intent before implementation.** Existing code is evidence, not automatically the specification.
2. **Provisional before blocked.** When selected as the import strategy, produce a useful draft before asking exhaustive questions.
3. **Questions by leverage.** Ask first about uncertainties with the greatest downstream effect.
4. **Files are authoritative.** Databases and indexes may accelerate the UI but do not replace the model files.
5. **Readable without special tooling.** A human or coding agent should understand the model by reading it.
6. **Stable identity, flexible organization.** Entities retain IDs when renamed or moved.
7. **Appearance is optional and granular.** Preserve it exactly only where the user intends.
8. **Changes are explicit and atomic.** AI analysis emits structured, validated transactions with visible effects and Undo rather than silently rewriting intent.
9. **Confirmed intent is protected.** Balanced mode stages AI-generated changes to confirmed or foundational behavior while allowing provisional exploration to remain fluid.
10. **Provenance follows the decision boundary.** Entities provide defaults, while independently reviewable Claims receive precise evidence and review metadata.
11. **Claims remain documents.** Normative behavior uses D+ Markdown sections with adjacent structured metadata rather than hiding prose in data structures.
12. **Confirmation follows content.** Editing confirmed Claim content makes its recorded confirmation stale until reconfirmed.

## Success criteria for the first usable slice

Given a small web application or prose specification, a user can:

1. obtain a plausible product frame and capability hierarchy;
2. inspect evidence certainty and review state for important claims;
3. answer one high-impact clarification question;
4. see the model and its files update coherently; and
5. hand the resulting directory to an external coding agent without extensive explanation.
