I evaluated Candidate X and Candidate Y as if seeing both for the first time, using the raw files and how they would appear in typical Git/Markdown review workflows.

## Scores

Scale: 1–5, where 5 is best.

| Criterion | Candidate X | Candidate Y |
|---|---|---|
| Human readability in raw and rendered Markdown | 5 | 2 |
| Coding-agent comprehension / editing reliability | 4 | 2.5 |
| Deterministic parser reliability / complexity | 2 | 5 |
| Git diff and merge quality | 4 | 3.5 |
| Resistance to duplicated truth / drift | 2.5 | 5 |
| Support for multiline Claims and rich provenance | 5 | 3 |
| Ease of adding, deleting, moving, reviewing Claims | 5 | 2 |
| Long-term format evolution | 2.5 | 5 |
| **Average** | **3.75** | **3.5** |

## Candidate X failure modes

- `title` appears both in YAML frontmatter and as an H1 in the body. These can drift.
- Claim statement boundaries are implicit. A literal heading or code fence inside a claim statement could be mis-parsed unless precise escaping rules are defined.
- Fenced `product-claim` blocks are associated positionally with the preceding `###` heading. Extra or misplaced fences can break parsing.
- Top-level `defaults.basedOn` uses a different schema shape than claim-level `provenance.basedOn`, which invites merge/schema confusion.
- No `formatVersion` field; future evolution is unversioned.
- Parsing requires a custom Markdown-aware parser rather than a simple YAML frontmatter extractor.

## Candidate Y failure modes

- All normative Claims and relationships live in YAML frontmatter, which many Markdown renderers hide or de-emphasize. A human reviewing the rendered Markdown sees only non-normative `## Context`; normative content is effectively invisible.
- Raw files become top-heavy YAML. Long claim statements need quoted or block scalars, reducing prose readability.
- YAML quoting and indentation are error-prone for coding agents. A missing space or incorrect nesting can produce invalid YAML or silently move a field under the wrong parent.
- Inserting or reordering claims inside nested YAML can create larger diffs and merge conflicts because indentation is syntactically meaningful.
- If a claim is accidentally written in the Markdown body, it is silently ignored unless a validator catches it. This creates a risk of phantom normative statements.
- `formatVersion: "0.1-experiment"` signals instability; a clear migration path is absent.

## Forced-choice winner

**Candidate X** is the better fit for the stated goal: the file must remain directly useful in Git and when handed to humans or coding agents without a dedicated UI.

Candidate X keeps the actual Claims and relationships visible as readable Markdown sections. Candidate Y centralizes normative data in frontmatter, which helps parser reliability but hides it from rendered Markdown review and makes raw editing more YAML-heavy.

## Constraints required to make Candidate X safe

To make Candidate X robust, the following constraints are required:

1. **Remove title duplication.** Keep `title` only in frontmatter or only in an H1, not both. The body should not repeat a canonical field.
2. **Define claim statement boundaries explicitly.** A claim’s statement is all Markdown content under its `### C{id}` heading until the next heading of any level or the start of a known metadata fenced block. Literal code fences inside a statement must use an explicit escape convention.
3. **Unify provenance schema.** Use the same nested shape everywhere, e.g. `defaults.provenance.basedOn`, not `defaults.basedOn`.
4. **Add a format version.** Include `formatVersion: "0.1"` at the top so parsers can evolve safely.
5. **Restrict fenced blocks.** Allow exactly one optional `product-claim` or `product-relationship` fenced block per item, and reject additional or misplaced blocks during validation.
6. **Validate aggressively.** Check for duplicate IDs, unknown fenced languages, misplaced fences, and non-metadata text after a metadata fence.
7. **Define merge semantics.** Claim-level provenance must override or extend defaults deterministically; `add` arrays should merge without duplicating entries.
8. **Keep one claim per section.** Do not allow multiple claims under one heading or shared body content.
9. **Discourage reformatting.** Git diffs should be line-preserving; editing one claim should not reformat unrelated claims.

Stale confirmation after a statement edit is a shared policy/validator issue. Neither syntax materially worsens it, because both separate the statement from its provenance.