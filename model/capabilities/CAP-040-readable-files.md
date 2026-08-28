---
id: CAP-040
type: capability
title: Represent the Product Model as readable files
parent: CAP-001
status: confirmed
relations:
  requires:
    - SUB-050
    - SUB-060
---

# Represent the Product Model as readable files

The user obtains an authoritative, Git-friendly directory that remains understandable without Product Modeler.

## Important behavior

- Entities retain stable IDs across renames and moves.
- Primary hierarchy and cross-tree dependencies are explicit.
- The format records provenance and uncertainty.
- Derived databases and graph indexes are rebuildable caches.
- The model can be validated for structural consistency.
