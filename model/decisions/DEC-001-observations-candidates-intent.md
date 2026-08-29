---
id: DEC-001
type: decision
title: Separate observations, candidate behaviors, and intended product entities
status: accepted
date: 2026-08-29
resolves:
  - Q-003
related:
  - CAP-020
  - CAP-030
  - SUB-030
---

# Separate observations, candidate behaviors, and intended product entities

Source analysis records granular Observations and groups them into Candidate Behaviors. Candidate Behaviors are offered for inclusion in the intended Product Model with a disposition of preserve, modify, exclude, or undecided.

Prototype import provides three initialization strategies:

- use the prototype as a starting point;
- start with an empty target;
- review candidates individually.

Selecting a candidate decides target intent; it does not change Evidence Certainty. The prototype-as-starting-point strategy is the default, and the user may use Select All, Select None, branch-level controls, or individual choices.

See [`../../docs/adr/0003-observations-candidates-and-intent.md`](../../docs/adr/0003-observations-candidates-and-intent.md).
