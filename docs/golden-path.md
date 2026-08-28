# Golden Path: Analyze and Clarify a Small Web Product

## Starting point

A user supplies a small React web-application repository. It contains routes, components, tests, styles, and local persistence, but no trustworthy product specification.

## Desired flow

1. The user creates an analysis project and selects the repository.
2. Product Modeler inventories the source evidence.
3. The AI produces a provisional Product Frame and capability hierarchy without waiting for exhaustive clarification.
4. The workspace displays the capability map beside a conversation panel.
5. The user selects a Capability and sees its definition, dependencies, evidence, and epistemic status.
6. The AI asks the highest-impact Clarification Question.
7. The user answers in chat.
8. The AI emits explicit structured mutations to the Product Model.
9. Changed nodes and relationships are highlighted in the map.
10. The corresponding text files are updated and remain readable outside the application.
11. The user reviews unresolved Inferences and exports or commits the Product Model for use by an external coding agent.

## Minimum generated model

The first analysis should produce:

- one Product Frame;
- one proposed Core Capability;
- several Supporting Capabilities;
- at least one Journey;
- discovered Interfaces and important Interface States;
- initial Domain Concepts;
- shared Subsystems and dependency links;
- provenance for consequential Claims;
- Clarification Questions ordered by impact.

## Acceptance example

Given the imported application contains routes for creating, viewing, and searching saved sources  
And source code suggests optional collections  
When analysis completes  
Then the model identifies saving and retrieving sources as candidate Capabilities  
And it records the collections conclusion as an Inference with source references  
And it asks whether collections are fundamental organization or an incidental prototype experiment.

When the user says collections are not part of the intended product  
Then the active model removes that inferred Capability  
And retains the rejected conclusion and its evidence in history  
And highlights affected Journeys and dependencies for review.

## Out of scope for this slice

- generating replacement application code;
- supporting non-web products;
- comprehensive framework support;
- multi-user collaboration;
- project planning or estimates;
- perfect visual reconstruction.

## Questions this scenario must force us to answer

- How does a Claim reference exact source evidence?
- Are AI mutations applied automatically or staged for acceptance?
- How are rejected Inferences retained without cluttering the active model?
- How much source context is stored versus referenced?
- How does the system decide which question has the greatest impact?
- What information must an external coding agent read first?
