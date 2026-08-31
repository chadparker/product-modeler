# D+ Claim Document Profile

Status: Experimental  
Format version: `0.1`

D+ is a Markdown-first profile for claim-bearing Product Model entities. Entity metadata and inherited defaults live in YAML frontmatter. Normative Claims are ordinary Markdown. Structured Claim and relationship metadata uses adjacent YAML fences.

## Document shape

````markdown
---
formatVersion: "0.1"
id: CAP-030
type: capability
parent: CAP-001
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
---

# Resolve consequential uncertainty

## Context

Non-normative explanatory prose.

## Claims

### C1

Normative Claim content in Markdown.

```product-claim
provenance:
  basedOn:
    add:
      - DEC-002
```

## Relationships

### R1

```product-relationship
type: requires
target: SUB-020
```
````

## Normative rules

1. Files are UTF-8 text without a byte-order mark. Parsers normalize CRLF and lone CR to LF.
2. The document starts with YAML frontmatter delimited by lines containing exactly `---`.
3. Frontmatter requires `formatVersion`, `id`, and `type`.
4. `formatVersion` is currently `"0.1"`.
5. The canonical entity title is the single level-one ATX heading. Frontmatter must not contain `title`. D+ recognizes CommonMark-style ATX headings with zero to three leading spaces, a space or tab after the marker, and an optional closing hash sequence.
6. Level-two sections may be `Context`, `Claims`, and `Relationships`, in that order. Each is optional and may occur at most once.
7. Context is non-normative.
8. Each Claim is a level-three heading containing only a stable local ID followed by non-empty Markdown content.
9. Claim content extends until an optional final `product-claim` fence or the next level-two or level-three heading outside a code fence.
10. A Claim may contain ordinary fenced code blocks. Fences follow the CommonMark rule allowing zero to three leading spaces, matching marker characters, and a closing marker at least as long as its opener. Unlike permissive Markdown rendering, D+ requires every fence to be explicitly closed so structural boundaries remain deterministic. A `product-claim` fence is reserved for metadata and must be the final nonblank content in its Claim. Reserved fence names are exact and case-sensitive; extra info-string words are invalid. Unknown or mis-cased `product-*` fence types are invalid anywhere in the document.
11. Each relationship is a level-three local-ID heading containing exactly one `product-relationship` YAML fence and no other content. The fence requires string fields `type` and `target`; `target` must use entity-ID syntax.
12. Local IDs match `[A-Z][A-Z0-9]*` and are unique across Claims and relationships in the entity.
13. Absence of a Claim override means inheritance. The literal value `inherited` is not stored.
14. Unknown metadata keys are preserved for forward compatibility.
15. YAML duplicate keys, aliases, anchors, explicit tags, merge keys, and non-JSON value types are invalid. Mapping keys must be strings. Implicit scalar resolution follows JSON-compatible forms: lowercase `true`, `false`, and `null`, decimal numbers without YAML-specific notation, and otherwise strings. Non-finite numbers are invalid.

## Provenance inheritance

Entity defaults may provide a base list:

```yaml
defaults:
  provenance:
    basedOn:
      - SRC-001
```

A Claim or relationship may replace it with a list:

```yaml
provenance:
  basedOn:
    - DEC-002
```

Or patch it explicitly:

```yaml
provenance:
  basedOn:
    add:
      - DEC-002
    remove:
      - SRC-001
```

Patch order is: begin with defaults, remove listed IDs, then append new IDs in declared order while suppressing duplicates.

## Review and stale confirmation

Review metadata has this shape:

```yaml
review:
  state: provisional
```

Allowed states are `provisional`, `confirmed`, `questioned`, and `proposed`.

Confirmation is Claim-specific. `defaults.review.state` must not be `confirmed`, and `defaults.review` must not contain `contentDigest`. A confirmed Claim must include its own content digest:

```yaml
review:
  state: confirmed
  contentDigest: sha256:<hexadecimal-digest>
```

The digest is SHA-256 over normalized Claim Markdown. The hashed content excludes the `### <local-id>` heading and excludes the trailing `product-claim` metadata fence:

1. normalize CRLF and lone CR to LF;
2. remove spaces and tabs at the end of every line;
3. remove leading and trailing lines that are empty after step 2;
4. join the remaining lines with LF and no final LF;
5. hash the UTF-8 bytes.

Golden digest vector:

```text
Claim Markdown: Clarification Questions do not block creation of the first provisional model.
Digest: sha256:cf9c7d7595ce49b72022b40d0b8fc2e3e91f8627840c4856d10e30a5fe514b64
```

If current content does not match `contentDigest`, validation reports a stale confirmation.

Relationships may be confirmed without a content digest because their normative content is their structured metadata.

## Parser behavior

Structural errors prevent parsing. Semantic validation reports invalid reference syntax, unsupported review states, malformed provenance patches, missing confirmation digests, and stale confirmation. Resolving whether referenced IDs exist is a repository-level validation responsibility.

The reference parser is in [`../reference_parser/`](../reference_parser/).
