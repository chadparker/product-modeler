from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from product_model_parser import DPlusError, parse_file, parse_text
from product_model_parser.parser import claim_digest


REPO_ROOT = Path(__file__).resolve().parents[2]


def document(body: str, frontmatter: str | None = None) -> str:
    frontmatter = frontmatter or """
formatVersion: "0.1"
id: CAP-030
type: capability
defaults:
  review:
    state: provisional
  provenance:
    basedOn:
      - SRC-001
"""
    return (
        "---\n"
        + textwrap.dedent(frontmatter).strip()
        + "\n---\n\n# Resolve consequential uncertainty\n\n"
        + textwrap.dedent(body).strip()
        + "\n"
    )


class ParserTests(unittest.TestCase):
    def test_parses_d_plus_experiment(self) -> None:
        path = REPO_ROOT / "format/experiments/claim-syntax/variant-d-plus.md"
        parsed = parse_file(path)
        self.assertTrue(parsed.valid, parsed.diagnostics)
        self.assertEqual(parsed.title, "Resolve consequential uncertainty")
        self.assertEqual([item.id for item in parsed.claims], ["C1", "C2", "C3", "C4"])
        self.assertEqual([item.id for item in parsed.relationships], ["R1", "R2"])
        self.assertEqual(parsed.claims[0].effective_based_on, ["SRC-001"])
        self.assertEqual(parsed.claims[2].effective_based_on, ["SRC-001", "DEC-002"])
        self.assertEqual(parsed.relationships[0].target, "SUB-020")

    def test_claim_supports_multiline_markdown_and_ordinary_fences(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                Users can inspect an example:

                - first item
                - second item

                ````markdown
                ```example
                nested
                ```
                ````
                """
            )
        )
        self.assertTrue(parsed.valid, parsed.diagnostics)
        self.assertIn("- first item", parsed.claims[0].markdown)
        self.assertIn("```example", parsed.claims[0].markdown)

    def test_claim_metadata_must_be_final(self) -> None:
        with self.assertRaisesRegex(DPlusError, "final nonblank content"):
            parse_text(
                document(
                    """
                    ## Claims

                    ### C1

                    A Claim.

                    ```product-claim
                    review:
                      state: proposed
                    ```

                    Extra prose.
                    """
                )
            )

    def test_relationship_may_only_contain_metadata(self) -> None:
        with self.assertRaisesRegex(DPlusError, "may contain only"):
            parse_text(
                document(
                    """
                    ## Relationships

                    ### R1

                    Requires search.

                    ```product-relationship
                    type: requires
                    target: SUB-020
                    ```
                    """
                )
            )

    def test_rejects_duplicate_yaml_keys(self) -> None:
        with self.assertRaisesRegex(DPlusError, "duplicate key"):
            parse_text(
                document(
                    "## Context\n\nNothing.",
                    """
                    formatVersion: "0.1"
                    id: CAP-030
                    id: CAP-031
                    type: capability
                    """,
                )
            )

    def test_rejects_yaml_aliases(self) -> None:
        with self.assertRaisesRegex(DPlusError, "anchors are not allowed|aliases are not allowed"):
            parse_text(
                document(
                    "## Context\n\nNothing.",
                    """
                    formatVersion: "0.1"
                    id: CAP-030
                    type: capability
                    shared: &shared
                      - SRC-001
                    copy: *shared
                    """,
                )
            )

    def test_title_must_not_be_duplicated_in_frontmatter(self) -> None:
        with self.assertRaisesRegex(DPlusError, "title belongs"):
            parse_text(
                document(
                    "## Context\n\nNothing.",
                    """
                    formatVersion: "0.1"
                    id: CAP-030
                    type: capability
                    title: Wrong place
                    """,
                )
            )

    def test_local_ids_must_be_unique_across_claims_and_relationships(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### X1

                A Claim.

                ## Relationships

                ### X1

                ```product-relationship
                type: requires
                target: SUB-020
                ```
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("id.duplicate", [item.code for item in parsed.diagnostics])

    def test_provenance_patch_removes_then_adds_without_duplicates(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.

                ```product-claim
                provenance:
                  basedOn:
                    remove:
                      - SRC-001
                    add:
                      - DEC-002
                      - DEC-002
                ```
                """
            )
        )
        self.assertTrue(parsed.valid, parsed.diagnostics)
        self.assertEqual(parsed.claims[0].effective_based_on, ["DEC-002"])

    def test_confirmed_claim_requires_digest(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A confirmed Claim.

                ```product-claim
                review:
                  state: confirmed
                ```
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("review.digest-missing", [item.code for item in parsed.diagnostics])

    def test_matching_confirmation_digest_is_valid(self) -> None:
        statement = "A confirmed Claim."
        digest = claim_digest(statement)
        parsed = parse_text(
            document(
                f"""
                ## Claims

                ### C1

                {statement}

                ```product-claim
                review:
                  state: confirmed
                  contentDigest: {digest}
                ```
                """
            )
        )
        self.assertTrue(parsed.valid, parsed.diagnostics)

    def test_changed_confirmed_claim_is_stale(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                Changed statement.

                ```product-claim
                review:
                  state: confirmed
                  contentDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                ```
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("review.stale", [item.code for item in parsed.diagnostics])

    def test_confirmed_review_cannot_be_inherited(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.
                """,
                """
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                defaults:
                  review:
                    state: confirmed
                """,
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("review.confirmed-default", [item.code for item in parsed.diagnostics])

    def test_unknown_reserved_fence_is_rejected(self) -> None:
        with self.assertRaisesRegex(DPlusError, "unsupported reserved fence"):
            parse_text(
                document(
                    """
                    ## Claims

                    ### C1

                    A Claim.

                    ```product-future
                    value: true
                    ```
                    """
                )
            )

    def test_indented_fence_protects_headings_inside_code(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                Example:

                   ```text
                ### NOT_A_CLAIM
                code
                   ```
                """
            )
        )
        self.assertTrue(parsed.valid, parsed.diagnostics)
        self.assertEqual([item.id for item in parsed.claims], ["C1"])
        self.assertIn("### NOT_A_CLAIM", parsed.claims[0].markdown)

    def test_four_space_marker_does_not_close_fence(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                ```text
                    ```
                ### STILL_CODE
                ```
                """
            )
        )
        self.assertTrue(parsed.valid, parsed.diagnostics)
        self.assertEqual([item.id for item in parsed.claims], ["C1"])
        self.assertIn("### STILL_CODE", parsed.claims[0].markdown)

    def test_confirmed_claim_cannot_inherit_digest(self) -> None:
        digest = claim_digest("A confirmed Claim.")
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A confirmed Claim.

                ```product-claim
                review:
                  state: confirmed
                ```
                """,
                f"""
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                defaults:
                  review:
                    state: provisional
                    contentDigest: {digest}
                """,
            )
        )
        self.assertFalse(parsed.valid)
        codes = [item.code for item in parsed.diagnostics]
        self.assertIn("review.digest-default", codes)
        self.assertIn("review.digest-missing", codes)

    def test_rejects_explicit_yaml_tags(self) -> None:
        with self.assertRaisesRegex(DPlusError, "explicit YAML tags are not allowed"):
            parse_text(
                document(
                    "## Context\n\nNothing.",
                    """
                    formatVersion: "0.1"
                    id: !!str CAP-030
                    type: capability
                    """,
                )
            )

    def test_reserved_product_fence_is_rejected_in_context(self) -> None:
        with self.assertRaisesRegex(DPlusError, "not allowed in Context"):
            parse_text(
                document(
                    """
                    ## Context

                    ```product-future
                    value: true
                    ```
                    """
                )
            )

    def test_present_null_values_are_invalid_not_inherited(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.

                ```product-claim
                provenance:
                  basedOn: null
                ```
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("provenance.basedOn.type", [item.code for item in parsed.diagnostics])

    def test_reference_syntax_is_validated(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Relationships

                ### R1

                ```product-relationship
                type: requires
                target: not-an-id
                provenance:
                  basedOn:
                    - also-bad
                ```
                """,
                """
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                parent: bad-parent
                """,
            )
        )
        self.assertFalse(parsed.valid)
        self.assertGreaterEqual([item.code for item in parsed.diagnostics].count("reference.format"), 3)

    def test_bom_is_rejected_explicitly(self) -> None:
        with self.assertRaisesRegex(DPlusError, "BOM is not allowed"):
            parse_text("\ufeff" + document("## Context\n\nNothing."))

    def test_duplicate_ids_within_section_are_validation_errors(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                First.

                ### C1

                Second.
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("id.duplicate", [item.code for item in parsed.diagnostics])

    def test_commonmark_atx_heading_forms_are_recognized(self) -> None:
        text = document(
            """
              ## Claims ##

              ### C1 ###

              First.

            ###\tC2

            Second.
            """
        ).replace("# Resolve consequential uncertainty", "  #\tResolve consequential uncertainty #")
        parsed = parse_text(text)
        self.assertTrue(parsed.valid, parsed.diagnostics)
        self.assertEqual(parsed.title, "Resolve consequential uncertainty")
        self.assertEqual([item.id for item in parsed.claims], ["C1", "C2"])

    def test_present_null_review_state_and_parent_are_invalid(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.

                ```product-claim
                review:
                  state: null
                ```
                """,
                """
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                parent: null
                """,
            )
        )
        self.assertFalse(parsed.valid)
        codes = [item.code for item in parsed.diagnostics]
        self.assertIn("review.state", codes)
        self.assertIn("reference.format", codes)

    def test_reserved_fence_names_are_exact(self) -> None:
        for fence in ("product-claim yaml", "Product-claim"):
            with self.subTest(fence=fence):
                with self.assertRaisesRegex(DPlusError, "unsupported reserved fence"):
                    parse_text(
                        document(
                            f"""
                            ## Claims

                            ### C1

                            A Claim.

                            ```{fence}
                            review:
                              state: proposed
                            ```
                            """
                        )
                    )

    def test_remove_patch_references_are_validated(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.

                ```product-claim
                provenance:
                  basedOn:
                    remove:
                      - not-an-id
                ```
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("reference.format", [item.code for item in parsed.diagnostics])

    def test_yaml_implicit_scalars_use_json_compatible_resolution(self) -> None:
        parsed = parse_text(
            document(
                "## Context\n\nNothing.",
                """
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                extensions:
                  yesValue: yes
                  octalLike: 012
                  timeLike: 12:30
                  dateLike: 2026-08-31
                  infinity: .inf
                  jsonBool: true
                  jsonNull: null
                  jsonInt: 12
                  jsonFloat: 1.5e2
                """,
            )
        )
        values = parsed.metadata["extensions"]
        self.assertEqual(values["yesValue"], "yes")
        self.assertEqual(values["octalLike"], "012")
        self.assertEqual(values["timeLike"], "12:30")
        self.assertEqual(values["dateLike"], "2026-08-31")
        self.assertEqual(values["infinity"], ".inf")
        self.assertIs(values["jsonBool"], True)
        self.assertIsNone(values["jsonNull"])
        self.assertEqual(values["jsonInt"], 12)
        self.assertEqual(values["jsonFloat"], 150.0)

    def test_digest_on_nonconfirmed_claim_is_invalid(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.

                ```product-claim
                review:
                  state: questioned
                  contentDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                ```
                """
            )
        )
        self.assertFalse(parsed.valid)
        self.assertIn("review.digest-unexpected", [item.code for item in parsed.diagnostics])

    def test_invalid_default_digest_is_not_propagated(self) -> None:
        parsed = parse_text(
            document(
                """
                ## Claims

                ### C1

                A Claim.
                """,
                """
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                defaults:
                  review:
                    state: provisional
                    contentDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                """,
            )
        )
        self.assertFalse(parsed.valid)
        self.assertNotIn("contentDigest", parsed.claims[0].effective_review)

    def test_frontmatter_diagnostics_preserve_nested_key_lines(self) -> None:
        parsed = parse_text(
            document(
                "## Context\n\nNothing.",
                """
                formatVersion: "0.1"
                id: CAP-030
                type: capability
                parent: invalid
                defaults:
                  review:
                    state: confirmed
                  provenance:
                    basedOn:
                      - invalid
                """,
            )
        )
        diagnostics = {item.code: item for item in parsed.diagnostics if item.code != "reference.format"}
        parent_references = [
            item
            for item in parsed.diagnostics
            if item.code == "reference.format" and item.message.startswith("parent")
        ]
        self.assertEqual(parent_references[0].line, 5)
        self.assertEqual(diagnostics["review.confirmed-default"].line, 8)
        provenance_references = [
            item
            for item in parsed.diagnostics
            if item.code == "reference.format" and "basedOn" in item.message
        ]
        self.assertEqual(provenance_references[0].line, 10)

    def test_unknown_h2_section_is_rejected(self) -> None:
        with self.assertRaisesRegex(DPlusError, "unsupported level-two section"):
            parse_text(document("## Requirements\n\nSomething."))


if __name__ == "__main__":
    unittest.main()
