# Blind Format Review — Candidate X vs Candidate Y

**Candidate X** = single YAML document in frontmatter (claims, relationships, defaults, provenance all as nested YAML), plus a Markdown body explicitly marked non‑normative.

**Candidate Y** = thin YAML frontmatter (identity + defaults) plus a Markdown body where each Claim is a `###` heading with prose statement, and optional metadata carried in fenced `product-claim` / `product-relationship` YAML blocks.

I evaluated each against the stated constraint set: usable raw in Git, usable when handed to a human or a coding agent with no UI, small documented parser + optional validator allowed, no required rendering/generation step.

---

## 1. Human readability (raw and rendered)

**X — 6/10.** Raw YAML is compact and the whole model is visible in one tree, which is genuinely good for skimming structure. Two real problems:

- **Rendered view loss.** Most Markdown renderers either strip frontmatter entirely or dump it as a raw/preformatted block. GitHub renders simple frontmatter as a table but handles deep nesting (`claims → C3 → provenance → basedOn → add`) poorly. The realistic rendered outcome is: a reader sees the *non‑normative* Context section and none of the normative content, or sees it as an unstyled blob. That inverts the intended emphasis.
- **Statement text is a quoted scalar**, so prose is squeezed into YAML string rules. It reads as data, not as a claim.

**Y — 9/10.** Claims read as claims in both raw and rendered form. Heading anchors give per‑claim deep links for free. The metadata fences render as small code blocks — visually subordinate to the statement, which matches their semantic weight. Minor cost: metadata for a claim is visually detached from the statement by a fence boundary, and `### C1` headings are ID‑only, so the rendered table of contents is a list of opaque IDs rather than titles.

---

## 2. Coding-agent comprehension and editing reliability (no prior training)

**X — 8/10.** An agent that knows YAML knows this file. The containment is explicit: `claims.C3.provenance.basedOn.add`. There is no "where does the statement end" question. Failure modes are the standard YAML ones and they are real:

- Indentation corruption when inserting a claim, silently reparenting `provenance` under the wrong claim or promoting a claim to top level.
- Quote/escape errors: a statement containing `:` , `"` , or a leading `-` breaks or silently changes meaning.
- Agents frequently rewrite YAML through a serializer, which reorders keys, restyles quotes, and reflows the entire block — a semantically empty but enormous diff.
- Nothing in the file prevents an agent from "helpfully" restating claims in the Context prose.

**Y — 7/10.** Statement editing is maximally reliable: it is plain prose in a bounded region, and an agent editing "C3's statement" cannot corrupt C4. Metadata edits are small isolated YAML documents, so blast radius is tiny. The comprehension risk is the *implicit* rule that must be inferred:

- Which text is the statement? Everything from the heading to the next heading? To the first fence? Does prose *after* the fence count? Two agents will answer differently unless the rule is written down in the file or a sibling spec.
- An agent adding an explanatory note under `### C2` may unknowingly extend the normative statement.
- Nothing structurally prevents `### C2` appearing twice, or a claim heading nested under the wrong `##` section.
- If a statement ever needs to contain a fenced code block, naive fence matching breaks.

X is more *self-describing*; Y is more *edit-safe*. Y's ambiguities are all closable by a one‑page grammar; X's YAML hazards are intrinsic.

---

## 3. Deterministic parser reliability and implementation complexity

**X — 9.5/10.** One `yaml.safe_load` of the frontmatter and you are done. The body is ignored by definition. This is the smallest possible parser and the hardest to get wrong. Residual risk is only the frontmatter delimiter scan (a `---` inside a block scalar, or the second `---` in the document).

**Y — 6/10.** Still small, but meaningfully larger: split frontmatter, scan headings, enforce section context (`## Claims` vs `## Relationships`), extract IDs from heading text, delimit the statement region, find and parse tagged fences, then parse each fence as YAML. That is maybe 120–200 lines with a real edge-case suite. Specific determinism traps:

- Fence nesting inside statements.
- Heading level drift (`####` used by a human) silently dropping a claim.
- Setext headings, trailing whitespace, CRLF.
- A `product-claim` fence with no preceding claim heading, or two fences under one heading.
- Statement normalization: are trailing blank lines, hard breaks, and lists part of the canonical text? This must be pinned or hashes/IDs will churn.

X wins this category decisively.

---

## 4. Git diff and merge quality

**X — 7/10.** Adding a claim is a clean contiguous insertion. But: all claims live inside one nested mapping, so two branches appending claims collide in the same region and produce indentation-sensitive conflicts that are easy to resolve *wrongly* (a mis-resolved merge can reparent `provenance`). Long statements as block scalars reflow badly. Serializer-driven reformatting is the biggest practical risk — one agent commit can rewrite the entire frontmatter.

**Y — 9/10.** Claims are separated by blank lines and headings, which is close to the ideal shape for line-based merge. Two branches adding different claims usually auto-merge. Moving a claim is a clean block move. Statement edits diff as prose — a reviewer sees exactly the sentence that changed, which is the highest-value review signal in this whole system. Weakness: a conflict that lands across a fence boundary can leave an unterminated fence, which the parser must reject loudly.

---

## 5. Resistance to duplicated truth / statement–metadata drift

**X — 8.5/10.** Single normative container, and the file states the invariant in-band ("All normative Claims and relationships are represented exactly once in YAML frontmatter. This Markdown section is non-normative context."). That sentence is doing real work. Statement and its provenance are literally the same YAML node, so they cannot be separated by an edit. Residual risk: nothing *enforces* that the Context prose doesn't paraphrase claims, and there is no linkage between prose and IDs, so drift between prose and claims is invisible.

**Y — 7/10.** Still one statement per claim, and the metadata fence is physically adjacent. But the coupling is by *position*, not by containment: a bad merge, a heading-level typo, or a moved claim can orphan a `product-claim` fence or attach it to the wrong claim. Additionally, Y's body invites narrative prose around claims, so paraphrase-drift pressure is higher. It also lacks the explicit in-band "this is the only normative representation" statement that X carries; that should be added.

**Note on the carved-out issue:** stale `review: confirmed` after a statement edit is a shared policy gap in both. Y is *marginally* worse only because the confirmation metadata sits in a separate block from the text it confirms, so a prose-only edit produces a diff with no visual touch to the confirmation. This is small and fully closed by requiring a statement hash (see constraints). It does not change the ranking.

---

## 6. Multiline Claims and rich provenance

**X — 6/10.** Provenance is excellent — arbitrarily rich, uniformly nested, trivially validated. Multiline statements are the weak point: block scalars (`|`) work but are indentation-sensitive, hostile to Markdown content (lists, nested fences, blank lines), invisible in rendered view, and prone to being rewritten as folded or quoted scalars by serializers. A claim that needs a bullet list or an example block is painful here.

**Y — 9/10.** Multiline, multi-paragraph, list-bearing, example-bearing statements are the *native* case and cost nothing. Provenance is equally expressive since the fence contains ordinary YAML. Only caveat is the fence-in-statement collision, solved by mandating longer outer fences.

---

## 7. Adding, deleting, moving, reviewing Claims

**X — 7/10.** Add = insert a nested block at the right indentation (agent-hostile). Delete = remove a block (easy). Move = re-indent (risky). Review = read quoted YAML strings; adequate but low-signal, and reviewers must mentally reconstruct meaning from data.

**Y — 9/10.** Add = append a heading and a paragraph. Delete = remove a heading-to-heading span. Move = cut and paste a block; the parser output is order-independent. Review = read English. This is the strongest argument in Y's favor for the "handed to humans without a UI" requirement.

---

## 8. Long-term format evolution

**X — 9/10.** Schema evolution is a solved problem in a single YAML tree: add keys, nest, version. **X already carries `formatVersion`; Y does not** — that is a concrete, present gap in Y, not a hypothetical one. Migration scripts are trivial to write and verify against X.

**Y — 7.5/10.** Extensible via new `product-*` fence languages and new keys inside them, which is reasonably clean. The evolution risk is *structural*: every new construct forces a decision about "prose region or fence?", and each such decision adds a grammar rule the parser and every agent must know. Grammar rules accumulate faster than schema keys, and migrating body structure is harder than migrating a YAML tree.

---

## Scores

| # | Criterion | X | Y |
|---|---|---|---|
| 1 | Human readability (raw + rendered) | 6.0 | 9.0 |
| 2 | Agent comprehension / edit reliability | 8.0 | 7.0 |
| 3 | Parser determinism / complexity | 9.5 | 6.0 |
| 4 | Git diff and merge quality | 7.0 | 9.0 |
| 5 | Resistance to duplicated truth / drift | 8.5 | 7.0 |
| 6 | Multiline claims + rich provenance | 6.0 | 9.0 |
| 7 | Add / delete / move / review claims | 7.0 | 9.0 |
| 8 | Long-term evolution | 9.0 | 7.5 |
| | **Unweighted mean** | **7.63** | **7.94** |

Weighted to the stated priorities (readability-without-UI and agent editing weighted ×1.5; parser complexity ×1.0 since a small documented parser is explicitly permitted):

**X ≈ 7.6 · Y ≈ 8.1**

---

## Forced-choice winner: **Candidate Y**

The deciding factor is the explicit requirement that the artifact be *directly useful* to humans and agents with no UI and no rendering step. X fails this in the rendered path in a way that is not a matter of taste: in common renderers the normative content is hidden or mangled, and the only thing a human sees is the section the file itself labels non‑normative. X also makes multiline claims — an explicitly required capability — the awkward case rather than the natural one.

Y's disadvantages are real but bounded and closable by specification: its parser is larger but still small and testable, and its ambiguities are grammar gaps, not intrinsic properties. X's disadvantages (rendered invisibility, prose-in-scalars, serializer churn, indentation-sensitive merges) are intrinsic to putting prose inside a nested YAML tree and cannot be specified away.

This is a close call, not a rout. If the deployment reality were "this file is consumed almost entirely by tooling and rarely read rendered," X should win on criteria 3 and 8 alone.

---

## Constraints required to make Y safe

These are not optional polish; without them Y's advantage does not hold.

1. **Add `formatVersion` to the frontmatter.** Y currently lacks it. Parsers must refuse unknown major versions.
2. **Write and ship a one-page normative grammar**, and reference it from the file or a sibling `FORMAT.md`, specifically fixing:
   - Claim heading form: exactly `### <ID>` under `## Claims`; relationship heading form under `## Relationships`; ID regex pinned.
   - Statement region: all content from the heading to the next heading of any level **or** the first `product-*` fence, whichever comes first. Content after the fence and before the next heading is **an error**, not a statement continuation, not a comment. This single rule closes the largest agent-comprehension gap.
   - Statement normalization: trim leading/trailing blank lines, preserve internal Markdown verbatim, CRLF normalized. Pin it, because IDs and hashes depend on it.
   - At most one `product-claim` fence per claim; a fence with no preceding claim heading is an error.
   - Statements containing fenced blocks must use a longer outer fence (` ```` `). Parsers must match fence lengths, not assume three backticks.
3. **Ship the validator as mandatory in CI, not optional.** Y trades parser simplicity for structural looseness; CI is where that debt is paid. Minimum checks: unique IDs, no orphan fences, no unterminated fences, no content after a fence within a claim, no claim outside `## Claims`, every referenced target ID resolvable, unknown `product-*` languages rejected.
4. **Restore the in-band normativity statement** that X carries — one sentence near the top declaring that `### <ID>` blocks under `## Claims` are the sole normative representation and all other prose is non-normative. Cheap, and it measurably suppresses paraphrase drift by both humans and agents.
5. **Prohibit reformatters on this file type.** No YAML round-tripping of the fences, no Markdown prettifier reflow of statement paragraphs. Reflow destroys the prose-diff advantage that is Y's main win in review.
6. **Require a `statementHash` (or equivalent) in the claim metadata alongside `review`.** This is the shared stale-confirmation policy fix, but it is *load-bearing* for Y specifically, because it re-couples the confirmation to the statement text that Y separates by a fence boundary. Validator fails when hash ≠ computed hash of the normalized statement.
7. **One canonical ordering rule** (e.g. claims sorted by ID, or explicitly declared order-insensitive). Y's easy block moves become a diff-noise source otherwise.

**What would flip the verdict:** if constraints 2, 3, and 6 cannot be committed to and enforced, Y degrades quickly toward ambiguous prose with decorative metadata, and X becomes the safer choice on strength of criteria 3 and 5.