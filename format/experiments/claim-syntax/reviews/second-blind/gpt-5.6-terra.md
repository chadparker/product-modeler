Assumption: Candidate X is the Markdown-primary file with claim headings and fenced metadata; Candidate Y is the YAML-frontmatter-primary file.

| Criterion | X | Y |
|---|---:|---:|
| Raw and rendered Markdown readability | 9 | 6 |
| Agent comprehension/editing without training | 6 | 8 |
| Deterministic parsing / implementation simplicity | 5 | 9 |
| Git diff and merge quality | 7 | 8 |
| Preventing duplicated truth / metadata drift | 6 | 9 |
| Multiline Claims and rich provenance | 9 | 8 |
| Add/delete/move/review Claims | 8 | 8 |
| Long-term evolution | 6 | 9 |
| **Overall** | **7.0** | **8.1** |

## Candidate X

**Strengths**
- Excellent raw Markdown reading: Claims are visibly prose, with nearby metadata.
- Natural support for long, structured, or rich-text Claims.
- Reviewing a Claim reads like reviewing a document.
- Moving or deleting a Claim is straightforward as a section-level operation.

**Failure modes**
- Parsing depends on Markdown structure: heading levels, heading text, fence placement, fence language, and section boundaries all become syntax.
- A claim body can accidentally absorb a relationship, metadata fence, or following Claim if headings are malformed.
- “Adjacent metadata” is inherently harder to associate deterministically, especially if future syntax permits notes, examples, nested headings, or multiple fences.
- Defaults plus per-Claim `add` semantics require a nontrivial inheritance/merge model; readers may not know the effective provenance without resolving it.
- Markdown prose and structured metadata can drift semantically: a Claim may say one thing while its nearby provenance or relationship block is misplaced.
- Tooling must implement a restricted Markdown parser or a carefully specified structural scanner; generic Markdown AST behavior can vary.

**Particularly risky evolution**
- Introducing subclaims, examples, tables, attachments, comments, or multiple metadata types makes section ownership ambiguous unless the grammar becomes substantially more rigid.

## Candidate Y

**Strengths**
- One normative representation: statements, defaults, provenance, and relationships are all machine-addressable and represented once.
- YAML structure gives deterministic ownership: `claims.C3.provenance` cannot accidentally attach to C4.
- Easier validation, schema migration, reference checking, duplicate-ID detection, and default-resolution tooling.
- Better for coding agents: a clear object model is visible immediately, and edits can be localized.
- Git merges generally operate on distinct mapping entries rather than Markdown sections with potentially ambiguous boundaries.
- Non-normative Markdown context avoids duplicate normative Claims.

**Failure modes**
- Raw Markdown readability is weaker: the important content is YAML rather than prose.
- YAML has well-known editing hazards: indentation mistakes, duplicate keys, implicit scalar typing in permissive parsers, quoting inconsistencies, anchors/aliases, and multiline scalar syntax.
- Mapping order is technically not semantic in generic YAML, while Git review benefits from stable order. Without a canonical ordering policy, unrelated reorder churn is likely.
- Large multiline Claims become visually noisy in YAML block scalars and can be awkward to edit.
- Human reviewers may overlook a semantic change inside a quoted or folded scalar more readily than a Markdown paragraph.
- The statement “frontmatter is normative; Markdown is non-normative” must be enforced. Otherwise contributors will eventually treat context prose as authoritative.

## Forced-choice winner: Candidate Y

Candidate Y is safer as the canonical file format because deterministic structure, validation, and single-source-of-truth behavior matter more than Markdown-native presentation. It remains directly usable in Git and by agents without requiring rendering.

Candidate X is preferable only if rich human-authored prose is the primary artifact and the project is willing to impose a highly restrictive Markdown grammar plus robust parser/validator.

## Constraints required to make Candidate Y safe

1. **Use a strict YAML subset and schema.**
   - Reject duplicate keys.
   - Reject anchors, aliases, tags, merge keys, and arbitrary YAML types.
   - Use YAML 1.2-compatible scalar rules or require quoted strings where ambiguity is possible.

2. **Define canonical formatting.**
   - Fixed key order: document metadata, defaults, claims, relationships.
   - Stable Claim and relationship ordering, preferably explicit order or lexicographic IDs.
   - Fixed indentation and block-scalar conventions.
   - A formatter may be optional, but validator diagnostics should identify noncanonical structure.

3. **Specify inheritance exactly.**
   - Define whether `basedOn.add` is additive set union, ordered concatenation, or something else.
   - Define duplicate handling, removal/override behavior, and effective-provenance resolution.
   - Validator should expose effective values.

4. **Support long statements explicitly.**
   - Permit literal block scalars (`|-`) for multiline Claims.
   - Define whether line wrapping is semantic and preserve exact text where required.

5. **Treat Markdown context as explicitly non-normative.**
   - Do not repeat Claim statements there.
   - Validator should optionally detect claim-like duplicated text or references that imply normativity.

6. **Version migrations must be explicit.**
   - Require `formatVersion`.
   - Publish migration rules and compatibility behavior.
   - Do not silently reinterpret old fields.

7. **Validate references and IDs.**
   - Enforce unique Claim/relationship IDs, valid targets, allowed relationship types, and provenance source existence where resolvable.

Finally, stale `review: confirmed` after a Claim statement changes is a shared semantic policy problem. Neither syntax solves it inherently. A validator should define whether changing `statement` automatically requires review state reset or an explicit reconfirmation action.