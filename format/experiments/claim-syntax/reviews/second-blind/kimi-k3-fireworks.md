# Blind Comparison: Candidate X vs. Candidate Y

## Candidate X — All-normative YAML frontmatter + non-normative prose body

**Strengths**
- Single source of truth, explicitly declared ("represented exactly once"). Title exists in exactly one place.
- One grammar, one parse step: split on the first two `---` delimiters, hand to any stock YAML library. Deterministic, ~50 lines of parser, easy to spec.
- Frontmatter-data + free-body is a widely known convention (static-site generators), so coding agents handle it correctly *without* format-specific training. Edits are expressible as key paths (`claims.C3.statement`), which is unambiguous in instructions.
- Statement and metadata are structurally bound — provenance cannot become attached to the wrong claim.
- Provenance nesting is consistent: `defaults.provenance.basedOn` and `claims.Cn.provenance.basedOn` follow the same shape.
- `formatVersion` present; new keys are additive; migrations are scriptable YAML-to-YAML transforms.

**Concrete failure modes**
- If a human drops the quotes around a statement containing `: `, `#`, or a leading `*`, the parse breaks or silently changes meaning. YAML 1.1 loaders coerce `yes/no/on/off` tokens.
- Duplicate claim keys (`C3` twice) silently last-win in lenient parsers.
- Long flow scalars (as used here) produce unreadable one-line diffs; two branches editing *different sentences of the same claim* always conflict.
- No per-claim anchors in rendered views — reviewers cannot deep-link to `C3`.
- Any tool that round-trips the file (re-serializes YAML) reorders keys and strips comments → diff churn.
- Rendered frontmatter (e.g., GitHub's table view) crams long statements poorly.

## Candidate Y — Markdown-native claims with fenced metadata

**Strengths**
- Best-in-class raw *and* rendered readability: claims are prose under headings, navigable via TOC, deep-linkable anchors, GitHub rich diff.
- Multiline claims, lists, emphasis, and links in statements are native — no escaping, no block scalars.
- Sentence-per-line prose gives fine-grained diffs; intra-claim merges can succeed where X's one-line strings cannot.

**Concrete failure modes**
- **Duplicated title** (frontmatter `title` and `#` H1) — an agent or human edits one, they drift. This is the exact failure class dimension 5 measures, present in the sample file itself.
- **Schema inconsistency in the sample**: defaults use `basedOn:` bare, claims use `provenance: basedOn:`. Agents will propagate whichever shape they saw last.
- **Implicit claim grammar**: a claim is "heading + prose + optional fence," but nothing specifies where statement text ends, whether prose may follow the fence, or what a `###` inside a statement means. Without prior training on this convention, agents guess.
- **Identity lives in heading prose**: `C 1`, `C1.`, `c1`, or a duplicate `### C1` all parse "successfully" with wrong results; nothing machine-enforces ID format or uniqueness by default.
- **Fence collision**: a claim statement that legitimately contains a fenced code block collides with the metadata-fence extraction; info-string handling varies across Markdown implementations.
- **Move/copy hazard**: cutting a claim but leaving its fence behind attaches DEC-002 provenance to the *wrong* claim — misattributed provenance is worse than missing provenance.
- **Parser burden**: Markdown AST + segmentation rules + embedded YAML = two grammars plus association heuristics; behavior varies across CommonMark/GFM/other parsers; structural edits (adding a subsection under a claim) break extraction.
- Editor auto-format reflows prose → noisy diffs; heading renames break external anchor links.
- No `formatVersion` in the example.

## Scores (0–10)

| Dimension | X | Y | Decisive factor |
|---|---|---|---|
| 1. Readability (raw + rendered) | 6.5 | 9.0 | Y reads as a document; X renders as a cramped table |
| 2. Agent comprehension/editing | 8.5 | 6.0 | X uses a known convention + key-path edits; Y requires guessing an implicit grammar |
| 3. Parser determinism/complexity | 9.0 | 5.5 | One grammar vs. Markdown AST + fences + association rules |
| 4. Git diff/merge | 7.5 | 8.5 | Y: intra-statement merges; X: one-line-string conflicts (fixable, see constraints) |
| 5. Drift/duplication resistance | 9.0 | 6.5 | Y duplicates the title and has two provenance shapes in-sample |
| 6. Multiline claims / rich provenance | 7.0 | 9.0 | Native Markdown vs. block scalars |
| 7. Add/delete/move/review | 8.0 | 7.0 | Y's fence-left-behind misattribution hazard; X's compact review surface |
| 8. Long-term evolution | 8.5 | 6.0 | X: additive keys + version gate; Y: structure is entangled with presentation, no version marker |
| **Average** | **8.0** | **7.2** | |

## Forced-choice winner: **Candidate X**

Y wins the three human-centric dimensions, but the stated use case — Git-native, consumed and edited by coding agents with no dedicated UI and no format-specific training — is decided by dimensions 2, 3, 5, and 8, where X wins clearly. Y's advantages are achievable *within* X via constraints; X's advantages (one grammar, bound statement+metadata, no duplicated truth) are not achievable within Y without writing the very spec-and-tooling burden the brief tries to avoid.

## Constraints required to make X safe

1. **Strict YAML loading**: reject duplicate keys, reject tabs, forbid anchors/aliases (they create hidden coupling between claims).
2. **Statement style rule**: all statements use block scalars (`|`), one sentence per line. This single rule eliminates the quoting-error class, the long-line diff problem, and the intra-claim merge conflict problem — closing Y's dimensions 4 and 6 advantages.
3. **Parse-only tooling**: no tool may re-serialize the file; humans/agents own the bytes. This preserves key order, comments, and blank lines.
4. **Validator (optional, non-blocking)**: schema check, claim-ID format/uniqueness (`C\d+`), relationship-target existence, provenance-overlay well-formedness, unknown keys = warning (forward compatibility), `formatVersion` gate for migrations.
5. **Documented claim-reference convention** (`CAP-030/C3`) plus a trivial CLI to print one claim, compensating for the lack of file anchors.
6. **Retain the explicit normative/non-normative boundary statement** in the body.

## Shared policy issue: stale `review: confirmed`

Both candidates store review status in `defaults`, structurally decoupled from statement text, so neither auto-invalidates confirmation on edit. This needs an external mechanism in either case — e.g., per-claim review records pinned to a statement digest, flagged by the validator. Y modestly *increases exposure* (prose invites casual copy-edits by people and agents who may not register its normative status), but not enough to change the verdict; treat it as a shared policy requirement, not a differentiator.

## Conditions under which the verdict would flip

If the primary consumers were non-technical humans reviewing long-form prose claims, and a formal spec (single title source, canonical claim-ID encoding, fence grammar, consistent provenance nesting, `formatVersion`) plus a canonical parser were committed to, Y would be defensible. Absent that spec, X is the safer substrate.