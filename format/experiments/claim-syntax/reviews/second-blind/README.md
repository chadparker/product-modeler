# Second Blind Review: Variant A+ versus Variant D

Date: 2026-08-31

## Method

Four one-shot reviewers received the same evaluation prompt and two anonymously named files. They received no conversation history, prior findings, candidate names, or other reviewers' responses.

Presentation order was counterbalanced:

| Reviewer | Candidate X | Candidate Y |
|---|---|---|
| Claude Opus 5 | Variant A+ | Variant D |
| GPT-5.6 Terra | Variant D | Variant A+ |
| Kimi K3 | Variant A+ | Variant D |
| DeepSeek V4 Pro | Variant D | Variant A+ |

The prompt and complete raw responses are preserved in this directory.

## Forced-choice result

The review split evenly:

| Reviewer | Winner |
|---|---|
| Claude Opus 5 | Variant D |
| GPT-5.6 Terra | Variant A+ |
| Kimi K3 | Variant A+ |
| DeepSeek V4 Pro | Variant D |

**Result: 2–2.** There was no independent-review consensus.

## Areas of broad agreement

Variant A+ is stronger for:

- standard-parser simplicity;
- deterministic ownership of statements and metadata;
- schema validation and migration;
- resistance to misplaced metadata;
- structured editing by coding agents.

Variant D is stronger for:

- raw and rendered human readability;
- reviewing Claims as prose;
- multiline Markdown, lists, examples, and links;
- localized Git diffs and merges;
- direct adding, deleting, and moving of Claims.

All reviewers treated stale confirmation after statement edits as a shared policy problem rather than a decisive syntax difference.

## Variant D defects exposed by the blind review

The evaluated Variant D sample contained several correctable inconsistencies:

- missing `formatVersion`;
- title duplicated in frontmatter and the H1;
- entity defaults used `basedOn` directly while Claim overrides used `provenance.basedOn`;
- the normative Claim-content boundary was not defined in-band;
- metadata-fence and heading constraints were not yet formalized.

These defects reduced its agent and parser scores. They are not inherent to the Markdown-plus-fenced-metadata approach, but fixing them increases the amount of format grammar that must be documented and validated.

## Subsequent outcome

This review records the decision boundary as it stood on August 31, 2026. The project subsequently selected **D+**, produced the corrected profile in [`../../../../DPLUS.md`](../../../../DPLUS.md), implemented its reference parser, and completed the dogfood migration. The alternatives and raw reviews remain here as historical design evidence.
