# Analysis Method

The analysis order is a hierarchy of reasoning priority, not the literal sequence in which files are inspected. Source code, tests, routes, data definitions, styles, and runtime behavior may be collected in parallel.

## Reasoning structure

```text
Product Evidence
      │
      ▼
1. Product Frame
      │
      ▼
2. Core Capability
      │
      ▼
3. Supporting Capabilities
      │
      ├────────────────┬─────────────────┐
      ▼                ▼                 ▼
4A. Journeys      4B. Domain Model  4C. Enablers
      │                │                 │
      ▼                ▼                 ▼
5A. Interfaces    5B. Rules/States  5C. Subsystems
      │
      ▼
6. Appearance
```

Implementation evidence informs every level, but does not define the conceptual priority.

## 0. Inventory Product Evidence

Identify available specifications, routes, components, tests, APIs, storage models, assets, screenshots, and runtime observations. Record what each source can and cannot establish.

## 1. Establish the Product Frame

Infer the audience, problem, intended outcome, usage context, and scope boundaries. Treat uncertain conclusions as hypotheses and prioritize questions that could substantially reframe the product.

## 2. Identify the Core Capability

State the smallest user-visible ability that delivers the product's fundamental value. Avoid naming an interface, technology, or internal service as the Core Capability.

## 3. Decompose Supporting Capabilities

Identify meaningful user abilities that collectively support the Core Capability. Use one primary `supports` parent for readability while allowing cross-tree dependency relationships.

## 4. Analyze three connected branches

### 4A. Journeys

Describe how actors combine Capabilities to achieve outcomes. Journeys reveal missing transitions and incoherent combinations that a feature inventory cannot.

### 4B. Domain Model

Identify concepts and language meaningful to product behavior. Do not assume database or source-code names are the correct product terms.

### 4C. Enablers

Find shared functionality, external dependencies, and constraints required by multiple Capabilities. Preserve specific technology choices only when confirmed as constraints.

## 5. Deepen each branch

### 5A. Interfaces and states

Map Journeys to interactive surfaces, actions, entry and exit paths, validation, errors, and meaningful states.

### 5B. Rules and transitions

Record behavioral invariants, lifecycles, permissions, and consequences independent of a particular interface.

### 5C. Subsystems and dependencies

Identify shared responsibilities and link them to the Capabilities that require them.

## 6. Classify Appearance

Capture screenshots, assets, tokens, structural layout, and important visual states when available. Assign an exact, structural, adaptive, inspirational, or unspecified Preservation Policy at screen or region level.

## Question priority

Questions should be ordered by expected model impact:

1. audience, problem, and intended outcome;
2. Core Capability and scope boundaries;
3. critical Journeys;
4. Domain Concepts and behavioral rules;
5. shared dependencies and external systems;
6. Interface states;
7. appearance fidelity;
8. historical implementation details.

The analyzer should present a useful provisional model before asking exhaustive questions.
