from __future__ import annotations

import io
import json
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from product_model_parser import DPlusError
from product_model_parser.__main__ import main
from product_model_parser.repository import (
    FileKind,
    ReferenceKind,
    ReferenceResolution,
    _dependency_cycle_for_edge,
    _functional_graph_cycles,
    build_repository_index,
    load_repository,
    validate_repository_graph,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


class RepositoryDiscoveryTests(unittest.TestCase):
    def test_discovers_and_classifies_repository_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                type: product
                title: Example
                """,
            )
            write(
                root / "capabilities/CAP-001.md",
                """
                ---
                formatVersion: "0.1"
                id: CAP-001
                type: capability
                ---

                # Create the product model

                ## Claims

                ### C1

                The system creates a model.
                """,
            )
            write(
                root / "capabilities/CAP-002.md",
                """
                ---
                id: CAP-002
                type: capability
                title: Legacy capability
                ---

                # Legacy capability
                """,
            )
            write(root / "appearance/README.md", "# Appearance\n\nSupporting guidance.\n")
            write(root / "assets/example.txt", "support data\n")
            write(root / ".hidden/ignored.md", "# Hidden\n")

            repository = load_repository(root)

            self.assertEqual(
                [(item.path, item.kind) for item in repository.files],
                [
                    ("appearance/README.md", FileKind.SUPPORT),
                    ("assets/example.txt", FileKind.SUPPORT),
                    ("capabilities/CAP-001.md", FileKind.DPLUS),
                    ("capabilities/CAP-002.md", FileKind.LEGACY),
                    ("product.yaml", FileKind.MANIFEST),
                ],
            )
            self.assertEqual(repository.files[2].entity_id, "CAP-001")
            self.assertEqual(repository.files[3].entity_id, "CAP-002")
            self.assertEqual(repository.files[4].entity_id, "PROD-001")
            self.assertEqual(repository.counts[FileKind.DPLUS.value], 1)
            self.assertEqual(repository.counts[FileKind.SUPPORT.value], 2)
            self.assertFalse(repository.has_errors)

    def test_reports_invalid_and_unsupported_model_documents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "future.md",
                """
                ---
                formatVersion: "9.0"
                id: CAP-900
                type: capability
                ---

                # Future
                """,
            )
            write(
                root / "broken.md",
                """
                ---
                formatVersion: "0.1"
                id: CAP-001
                type: capability
                ---

                No title.
                """,
            )
            write(
                root / "bad/product.yaml",
                """
                formatVersion: "0.1"
                id: [not, a, string]
                type: product
                """,
            )

            repository = load_repository(root)
            by_path = {item.path: item for item in repository.files}

            self.assertEqual(by_path["future.md"].kind, FileKind.UNSUPPORTED)
            self.assertEqual(by_path["broken.md"].kind, FileKind.INVALID)
            self.assertEqual(by_path["bad/product.yaml"].kind, FileKind.INVALID)
            self.assertEqual(
                [item.code for item in repository.diagnostics],
                ["manifest.id", "manifest.title", "document.structure", "format.unsupported"],
            )
            self.assertTrue(repository.has_errors)
            for diagnostic in repository.diagnostics:
                self.assertIsNotNone(diagnostic.path)
                self.assertIsNotNone(diagnostic.line)

    def test_product_yaml_missing_type_is_invalid_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                title: Example
                """,
            )

            item = load_repository(root).files[0]

            self.assertEqual(item.kind, FileKind.INVALID)
            self.assertIn("manifest.type", [diagnostic.code for diagnostic in item.diagnostics])

    def test_semantic_diagnostics_point_to_key_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"

                id: [invalid]
                type: product
                title: Example
                """,
            )
            write(
                root / "CAP-001-legacy.md",
                """
                ---
                type: capability

                id: [invalid]
                ---

                # Legacy
                """,
            )

            repository = load_repository(root)
            diagnostics = {diagnostic.code: diagnostic for diagnostic in repository.diagnostics}

            self.assertEqual(diagnostics["manifest.id"].line, 3)
            self.assertEqual(diagnostics["legacy.id"].line, 4)

    def test_single_file_cli_reports_invalid_utf8_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.md"
            path.write_bytes(b"\xff\xfe")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main([str(path)])

            self.assertEqual(status, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("codec can't decode", stderr.getvalue())

    def test_json_and_digests_are_mutually_exclusive(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main(["--json", "--digests", "document.md"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("not allowed with argument", stderr.getvalue())

    def test_generic_frontmatter_and_yaml_are_support_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "guide.md",
                """
                ---
                id: introduction
                type: guide
                ---

                # Introduction
                """,
            )
            write(
                root / "settings.yaml",
                """
                id: local-settings
                type: development
                """,
            )
            write(root / "notes.md", "---\nid: [unfinished\n")
            write(root / "freeform.yaml", "- *undefined-alias\n")

            repository = load_repository(root)

            self.assertEqual(
                [item.kind for item in repository.files],
                [FileKind.SUPPORT, FileKind.SUPPORT, FileKind.SUPPORT, FileKind.SUPPORT],
            )
            self.assertFalse(repository.diagnostics)

    def test_file_symlinks_are_not_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            external = Path(outside) / "CAP-999-external.md"
            write(external, "# External\n")
            (root / "CAP-999-external.md").symlink_to(external)
            write(root / "README.md", "# Local\n")

            repository = load_repository(root)

            self.assertEqual([item.path for item in repository.files], ["README.md"])

    def test_valid_legacy_identity_does_not_require_filename_convention(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "historical-name.md",
                """
                ---
                id: CAP-123
                type: capability
                ---

                # Historical name
                """,
            )

            item = load_repository(root).files[0]

            self.assertEqual(item.kind, FileKind.LEGACY)
            self.assertEqual(item.entity_id, "CAP-123")

    def test_structural_and_manifest_diagnostics_include_known_addresses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "CAP-001.md",
                """
                ---
                formatVersion: "0.1"
                id: CAP-001
                type: capability
                ---

                Missing title.
                """,
            )
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                type: product
                """,
            )

            diagnostics = {item.code: item for item in load_repository(root).diagnostics}

            self.assertEqual(diagnostics["document.structure"].address, "CAP-001")
            self.assertEqual(diagnostics["manifest.title"].address, "PROD-001")

    def test_deep_yaml_is_reported_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = "[" * 1500 + "0" + "]" * 1500
            write(root / "product.yaml", f"nested: {payload}\n")

            repository = load_repository(root)

            self.assertEqual(repository.files[0].kind, FileKind.INVALID)
            self.assertEqual(repository.diagnostics[0].code, "manifest.yaml")
            self.assertIn("exceeds", repository.diagnostics[0].message)

    def test_huge_yaml_integer_is_reported_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            huge_integer = "9" * 5000
            write(
                root / "product.yaml",
                f"formatVersion: '0.1'\nid: {huge_integer}\ntype: product\ntitle: Example\n",
            )

            repository = load_repository(root)

            self.assertEqual(repository.files[0].kind, FileKind.INVALID)
            self.assertEqual(repository.diagnostics[0].code, "manifest.yaml")
            self.assertIn("exceeds", repository.diagnostics[0].message)

    def test_dplus_frontmatter_structure_errors_use_key_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "CAP-001.md",
                """
                ---
                formatVersion: "0.1"
                type: capability

                id: [invalid]
                ---

                # Capability
                """,
            )

            diagnostic = load_repository(root).diagnostics[0]

            self.assertEqual(diagnostic.code, "document.structure")
            self.assertEqual(diagnostic.line, 5)

    def test_exact_inspect_filename_uses_legacy_single_file_mode(self) -> None:
        stderr = io.StringIO()
        marker = DPlusError("parsed as a file", source="inspect", line=1)
        with patch("product_model_parser.__main__.parse_file", side_effect=marker) as parse_mock:
            with redirect_stderr(stderr):
                status = main(["inspect"])

        self.assertEqual(status, 1)
        parse_mock.assert_called_once_with(Path("inspect"))
        self.assertIn("parsed as a file", stderr.getvalue())

    def test_inline_yaml_comments_do_not_hide_dplus_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "historical-name.md",
                """
                ---
                formatVersion: "0.1" # current profile
                id: CAP-123 # stable identity
                type: capability # entity kind
                ---

                # Capability

                ## Claims

                ### C1

                A Claim.
                """,
            )

            item = load_repository(root).files[0]

            self.assertEqual(item.kind, FileKind.DPLUS)
            self.assertEqual(item.entity_id, "CAP-123")

    def test_recognized_legacy_type_without_id_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "historical-name.md",
                """
                ---
                type: capability
                ---

                # Capability
                """,
            )

            item = load_repository(root).files[0]

            self.assertEqual(item.kind, FileKind.INVALID)
            self.assertIn("legacy.id", [diagnostic.code for diagnostic in item.diagnostics])

    def test_entity_named_markdown_without_frontmatter_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / "CAP-001.md", "# Missing frontmatter\n")

            item = load_repository(root).files[0]

            self.assertEqual(item.kind, FileKind.INVALID)
            self.assertEqual(item.diagnostics[0].code, "document.structure")

    def test_unrelated_format_version_frontmatter_remains_support(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "guide.md",
                """
                ---
                formatVersion: "1.0"
                ---

                # Guide
                """,
            )

            item = load_repository(root).files[0]

            self.assertEqual(item.kind, FileKind.SUPPORT)
            self.assertFalse(item.diagnostics)

    def test_semantically_invalid_dplus_remains_classified_as_dplus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "CAP-001.md",
                """
                ---
                formatVersion: "0.1"
                id: CAP-001
                type: capability
                ---

                # Capability

                ## Claims

                ### C1

                A confirmed Claim.

                ```product-claim
                review:
                  state: confirmed
                ```
                """,
            )

            repository = load_repository(root)
            item = repository.files[0]
            self.assertEqual(item.kind, FileKind.DPLUS)
            self.assertIsNotNone(item.document)
            self.assertEqual([diag.code for diag in item.diagnostics], ["review.digest-missing"])
            self.assertTrue(repository.has_errors)

    def test_serialization_is_deterministic_and_json_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / "zeta/README.md", "# Zeta\n")
            write(root / "alpha/README.md", "# Alpha\n")

            repository = load_repository(root)
            first = repository.to_dict()
            second = load_repository(root).to_dict()

            self.assertEqual(first, second)
            self.assertEqual([item["path"] for item in first["files"]], ["alpha/README.md", "zeta/README.md"])
            json.dumps(first)

    def test_inspect_cli_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / "README.md", "# Support\n")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(["inspect", str(root), "--json"])

            self.assertEqual(status, 0)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["counts"]["support"], 1)
            self.assertEqual(payload["files"][0]["path"], "README.md")

    def test_classifies_current_dogfood_repository(self) -> None:
        repository = load_repository(REPO_ROOT / "model")

        self.assertEqual(repository.counts[FileKind.MANIFEST.value], 1)
        self.assertEqual(repository.counts[FileKind.LEGACY.value], 30)
        self.assertEqual(repository.counts[FileKind.SUPPORT.value], 3)
        self.assertEqual(repository.counts.get(FileKind.DPLUS.value, 0), 0)
        self.assertFalse(repository.has_errors, repository.diagnostics)


class RepositoryIndexTests(unittest.TestCase):
    def _write_legacy(self, root: Path, path: str, entity_id: str) -> None:
        write(
            root / path,
            f"""
            ---
            id: {entity_id}
            type: capability
            ---

            # {entity_id}
            """,
        )

    def _write_dplus(
        self,
        root: Path,
        path: str,
        entity_id: str,
        *,
        claim_id: str | None = None,
    ) -> None:
        claims = ""
        if claim_id is not None:
            claims = f"""

            ## Claims

            ### {claim_id}

            A Claim for {entity_id}.
            """
        write(
            root / path,
            f"""
            ---
            formatVersion: "0.1"
            id: {entity_id}
            type: capability
            ---

            # {entity_id}
            {claims}
            """,
        )

    def test_indexes_manifest_legacy_and_dplus_declarations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                type: product
                title: Example
                """,
            )
            self._write_legacy(root, "CAP-001.md", "CAP-001")
            self._write_dplus(root, "CAP-002.md", "CAP-002", claim_id="C1")

            index = build_repository_index(load_repository(root))

            self.assertEqual(set(index.entities_by_id), {"PROD-001", "CAP-001", "CAP-002"})
            self.assertEqual(set(index.claims_by_address), {"CAP-002#C1"})
            self.assertEqual(index.entities_by_file["product.yaml"].line, 2)
            self.assertEqual(index.entities_by_file["CAP-001.md"].line, 2)
            self.assertFalse(index.has_errors)

    def test_duplicate_legacy_entities_report_every_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_legacy(root, "a.md", "CAP-001")
            self._write_legacy(root, "z.md", "CAP-001")

            index = build_repository_index(load_repository(root))

            self.assertEqual(
                [item.path for item in index.entity_declarations["CAP-001"]],
                ["a.md", "z.md"],
            )
            self.assertEqual(
                [(item.path, item.code) for item in index.diagnostics],
                [("a.md", "entity.duplicate"), ("z.md", "entity.duplicate")],
            )
            self.assertIn("z.md:2", index.diagnostics[0].message)
            self.assertNotIn("CAP-001", index.entities_by_id)

    def test_duplicate_dplus_entities_report_entity_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_dplus(root, "a.md", "CAP-001")
            self._write_dplus(root, "b.md", "CAP-001")

            index = build_repository_index(load_repository(root))

            self.assertEqual(len(index.entity_declarations["CAP-001"]), 2)
            self.assertEqual(
                [item.code for item in index.diagnostics],
                ["entity.duplicate", "entity.duplicate"],
            )

    def test_legacy_and_dplus_ids_can_collide(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_legacy(root, "legacy.md", "CAP-001")
            self._write_dplus(root, "modern.md", "CAP-001")

            index = build_repository_index(load_repository(root))

            self.assertEqual(
                [item.kind for item in index.entity_declarations["CAP-001"]],
                [FileKind.LEGACY, FileKind.DPLUS],
            )
            self.assertNotIn("CAP-001", index.entities_by_id)

    def test_unsupported_file_with_recovered_id_participates_in_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_legacy(root, "legacy.md", "CAP-900")
            write(
                root / "future.md",
                """
                ---
                formatVersion: "9.0"
                id: CAP-900
                type: capability
                ---

                # Future
                """,
            )

            index = build_repository_index(load_repository(root))

            self.assertEqual(
                [item.kind for item in index.entity_declarations["CAP-900"]],
                [FileKind.UNSUPPORTED, FileKind.LEGACY],
            )
            self.assertEqual(
                [item.code for item in index.diagnostics],
                ["entity.duplicate", "entity.duplicate"],
            )

    def test_duplicate_entity_documents_create_duplicate_claim_addresses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_dplus(root, "a.md", "CAP-001", claim_id="C1")
            self._write_dplus(root, "b.md", "CAP-001", claim_id="C1")

            index = build_repository_index(load_repository(root))

            self.assertEqual(len(index.claim_declarations["CAP-001#C1"]), 2)
            self.assertNotIn("CAP-001#C1", index.claims_by_address)
            self.assertEqual(
                [item.code for item in index.diagnostics],
                [
                    "entity.duplicate",
                    "claim.duplicate",
                    "entity.duplicate",
                    "claim.duplicate",
                ],
            )

    def test_index_serialization_and_diagnostics_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_legacy(root, "z.md", "CAP-001")
            self._write_legacy(root, "a.md", "CAP-001")

            first = build_repository_index(load_repository(root)).to_dict()
            second = build_repository_index(load_repository(root)).to_dict()

            self.assertEqual(first, second)
            self.assertEqual([item["path"] for item in first["entities"]], ["a.md", "z.md"])
            json.dumps(first)

    def test_validate_cli_reports_duplicates_in_text_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_legacy(root, "a.md", "CAP-001")
            self._write_legacy(root, "b.md", "CAP-001")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                text_status = main(["validate", str(root)])

            self.assertEqual(text_status, 1)
            self.assertIn("2 entity declarations (0 unique)", stdout.getvalue())
            self.assertIn("entity.duplicate", stderr.getvalue())

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                json_status = main(["validate", str(root), "--json"])

            self.assertEqual(json_status, 1)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["hasErrors"])
            self.assertEqual(payload["counts"]["entityDeclarations"], 2)
            self.assertEqual(
                [item["code"] for item in payload["diagnostics"]].count("entity.duplicate"),
                2,
            )

    def test_validate_cli_allows_legacy_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                type: product
                title: Example
                coreCapability: CAP-001
                """,
            )
            write(
                root / "CAP-001.md",
                """
                ---
                id: CAP-001
                type: capability
                parent: null
                ---

                # CAP-001
                """,
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(["validate", str(root)])

            self.assertEqual(status, 0)
            self.assertIn("file.legacy", stderr.getvalue())

    def test_entity_declaration_lines_follow_explicit_yaml_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                ? id
                : PROD-001
                formatVersion: "0.1"
                type: product
                title: Example
                """,
            )
            write(
                root / "CAP-001.md",
                """
                ---
                ? id
                : CAP-001
                formatVersion: "0.1"
                type: capability
                ---

                # Capability
                """,
            )

            index = build_repository_index(load_repository(root))

            self.assertEqual(index.entities_by_id["PROD-001"].line, 2)
            self.assertEqual(index.entities_by_id["CAP-001"].line, 3)

    def test_flow_style_metadata_is_discovered_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "historical.md",
                """
                ---
                {id: CAP-001, type: capability}
                ---

                # Historical
                """,
            )
            write(root / "future.yaml", "{id: CAP-002, type: capability}\n")

            repository = load_repository(root)
            index = build_repository_index(repository)

            self.assertEqual(
                {item.path: item.kind for item in repository.files},
                {
                    "future.yaml": FileKind.UNSUPPORTED,
                    "historical.md": FileKind.LEGACY,
                },
            )
            self.assertEqual(set(index.entities_by_id), {"CAP-001", "CAP-002"})

    def test_explicit_yaml_diagnostics_use_actual_key_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "future.md",
                """
                ---
                type: capability
                ? formatVersion
                : "9.0"
                id: CAP-001
                ---

                # Future
                """,
            )
            write(
                root / "future.yaml",
                """
                id: CAP-002
                ? formatVersion
                : "9.0"
                type: capability
                """,
            )

            diagnostics = {
                item.path: item
                for item in load_repository(root).diagnostics
                if item.code == "format.unsupported"
            }

            self.assertEqual(diagnostics["future.md"].line, 3)
            self.assertEqual(diagnostics["future.yaml"].line, 2)

    def test_document_local_claim_duplicates_do_not_get_repository_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "CAP-001.md",
                """
                ---
                formatVersion: "0.1"
                id: CAP-001
                type: capability
                ---

                # Capability

                ## Claims

                ### C1

                First.

                ### C1

                Second.
                """,
            )

            repository = load_repository(root)
            index = build_repository_index(repository)

            self.assertIn("id.duplicate", [item.code for item in repository.diagnostics])
            self.assertEqual(len(index.claim_declarations["CAP-001#C1"]), 2)
            self.assertNotIn("CAP-001#C1", index.claims_by_address)
            self.assertNotIn("claim.duplicate", [item.code for item in index.diagnostics])

    def test_validate_without_directory_reports_cli_usage_error(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main(["validate"])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("directory", stderr.getvalue())

    def test_indexes_current_dogfood_repository_without_duplicates(self) -> None:
        repository = load_repository(REPO_ROOT / "model")
        index = build_repository_index(repository)

        self.assertEqual(sum(len(items) for items in index.entity_declarations.values()), 31)
        self.assertEqual(len(index.entities_by_id), 31)
        self.assertEqual(index.claim_declarations, {})
        self.assertFalse(index.has_errors, index.diagnostics)


class RepositoryReferenceTests(unittest.TestCase):
    def _write_entity(
        self,
        root: Path,
        path: str,
        entity_id: str,
        entity_type: str,
        extra: str = "",
    ) -> None:
        write(
            root / path,
            f"""
            ---
            id: {entity_id}
            type: {entity_type}
            {extra}
            ---

            # {entity_id}
            """,
        )

    def _write_relationship_document(
        self,
        root: Path,
        path: str,
        entity_id: str,
        target: str,
        *,
        defaults: str = "",
    ) -> None:
        defaults_block = textwrap.dedent(defaults).strip()
        frontmatter_extra = f"{defaults_block}\n" if defaults_block else ""
        write(
            root / path,
            f"---\n"
            f"formatVersion: \"0.1\"\n"
            f"id: {entity_id}\n"
            f"type: capability\n"
            f"{frontmatter_extra}"
            f"---\n\n"
            f"# {entity_id}\n\n"
            f"## Claims\n\n"
            f"### C1\n\n"
            f"A Claim.\n\n"
            f"## Relationships\n\n"
            f"### R1\n\n"
            f"```product-relationship\n"
            f"type: requires\n"
            f"target: {target}\n"
            f"```\n",
        )

    def test_resolves_dplus_relationships_into_incoming_and_outgoing_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_entity(root, "target.md", "CAP-001", "capability")
            self._write_relationship_document(root, "source.md", "CAP-002", "CAP-001")

            index = build_repository_index(load_repository(root))
            reference = index.outgoing_references["CAP-002#R1"][0]

            self.assertEqual(reference.kind, ReferenceKind.RELATIONSHIP)
            self.assertEqual(reference.relationship_type, "requires")
            self.assertEqual(reference.resolution, ReferenceResolution.RESOLVED)
            self.assertEqual(index.incoming_references["CAP-001"], (reference,))
            self.assertFalse(index.has_errors)

    def test_missing_and_ambiguous_targets_are_diagnosed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_relationship_document(root, "missing.md", "CAP-002", "SUB-999")
            self._write_entity(root, "a.md", "CAP-001", "capability")
            self._write_entity(root, "b.md", "CAP-001", "capability")
            self._write_relationship_document(root, "ambiguous.md", "CAP-003", "CAP-001")

            index = build_repository_index(load_repository(root))
            by_source = {item.source_address: item for item in index.references}

            self.assertEqual(by_source["CAP-002#R1"].resolution, ReferenceResolution.MISSING)
            self.assertEqual(by_source["CAP-003#R1"].resolution, ReferenceResolution.AMBIGUOUS)
            self.assertIn("reference.missing", [item.code for item in index.diagnostics])
            self.assertIn("reference.ambiguous", [item.code for item in index.diagnostics])

    def test_unusable_unique_targets_are_not_marked_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "future.md",
                """
                ---
                formatVersion: "9.0"
                id: CAP-900
                type: capability
                ---

                # Future
                """,
            )
            self._write_relationship_document(root, "source.md", "CAP-001", "CAP-900")

            index = build_repository_index(load_repository(root))
            reference = next(item for item in index.references if item.target_id == "CAP-900")

            self.assertEqual(reference.resolution, ReferenceResolution.UNAVAILABLE)
            self.assertIn("reference.unavailable", [item.code for item in index.diagnostics])

    def test_indexes_effective_claim_and_relationship_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_entity(root, "source.md", "SRC-001", "source")
            self._write_entity(root, "target.md", "CAP-001", "capability")
            self._write_relationship_document(
                root,
                "document.md",
                "CAP-002",
                "CAP-001",
                defaults="""
                defaults:
                  provenance:
                    basedOn:
                      - SRC-001
                """,
            )

            index = build_repository_index(load_repository(root))
            provenance = [item for item in index.references if item.kind == ReferenceKind.PROVENANCE]

            self.assertEqual(
                [(item.source_address, item.target_id) for item in provenance],
                [("CAP-002#C1", "SRC-001"), ("CAP-002#R1", "SRC-001")],
            )
            self.assertEqual(len(index.incoming_references["SRC-001"]), 2)

    def test_builds_capability_parent_and_children_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                type: product
                title: Example
                coreCapability: CAP-001
                """,
            )
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", "parent: null")
            self._write_entity(root, "CAP-002.md", "CAP-002", "capability", "parent: CAP-001")

            index = build_repository_index(load_repository(root))

            self.assertEqual(index.capability_parents, {"CAP-002": "CAP-001"})
            self.assertEqual(index.capability_children, {"CAP-001": ("CAP-002",)})
            self.assertEqual(
                index.outgoing_references["PROD-001"][0].kind,
                ReferenceKind.CORE_CAPABILITY,
            )
            self.assertFalse(index.has_errors)

    def test_capability_parent_rules_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "product.yaml",
                """
                formatVersion: "0.1"
                id: PROD-001
                type: product
                title: Example
                coreCapability: CAP-001
                """,
            )
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", "parent: CAP-002")
            self._write_entity(root, "CAP-002.md", "CAP-002", "capability", "parent: null")
            self._write_entity(root, "CAP-003.md", "CAP-003", "capability", "parent: SUB-001")
            self._write_entity(root, "SUB-001.md", "SUB-001", "subsystem")

            index = build_repository_index(load_repository(root))
            codes = [item.code for item in index.diagnostics]

            self.assertIn("capability.parent-root", codes)
            self.assertIn("capability.parent-required", codes)
            self.assertIn("capability.parent-type", codes)
            self.assertNotIn("CAP-001", index.capability_parents)
            self.assertNotIn("CAP-001", index.capability_children.get("CAP-002", ()))

    def test_indexes_legacy_relationship_and_source_references_with_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_entity(root, "SRC-001.md", "SRC-001", "source")
            self._write_entity(root, "SUB-001.md", "SUB-001", "subsystem")
            write(
                root / "CAP-001.md",
                """
                ---
                id: CAP-001
                type: capability
                provenance:
                  - source: SRC-001
                relations:
                  requires:
                    - SUB-001
                ---

                # Capability
                """,
            )

            index = build_repository_index(load_repository(root))
            references = index.outgoing_references["CAP-001"]

            self.assertEqual(
                [(item.kind, item.target_id, item.line) for item in references],
                [
                    (ReferenceKind.PROVENANCE, "SRC-001", 5),
                    (ReferenceKind.RELATIONSHIP, "SUB-001", 8),
                ],
            )

    def test_malformed_legacy_reference_structures_are_diagnosed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "CAP-001.md",
                """
                ---
                id: CAP-001
                type: capability
                provenance:
                  - kind: confirmation
                relations:
                  - requires
                related: CAP-002
                sources: null
                capabilities: null
                ---

                # Capability
                """,
            )

            index = build_repository_index(load_repository(root))
            diagnostics = [item for item in index.diagnostics if item.code == "reference.structure"]

            self.assertEqual(len(diagnostics), 5)
            self.assertEqual([item.line for item in diagnostics], [5, 7, 8, 9, 10])

    def test_semantically_typed_legacy_references_validate_target_types(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability")
            self._write_entity(root, "SUB-001.md", "SUB-001", "subsystem")
            write(
                root / "Q-001.md",
                """
                ---
                id: Q-001
                type: question
                resolvedBy: CAP-001
                ---

                # Question
                """,
            )
            write(
                root / "DEC-001.md",
                """
                ---
                id: DEC-001
                type: decision
                resolves:
                  - CAP-001
                ---

                # Decision
                """,
            )
            write(
                root / "UI-001.md",
                """
                ---
                id: UI-001
                type: interface
                capabilities:
                  - SUB-001
                ---

                # Interface
                """,
            )

            diagnostics = build_repository_index(load_repository(root)).diagnostics
            type_diagnostics = [item for item in diagnostics if item.code == "reference.type"]

            self.assertEqual(len(type_diagnostics), 3)
            self.assertEqual(
                {item.address for item in type_diagnostics},
                {"Q-001", "DEC-001", "UI-001"},
            )

    def test_legacy_reference_syntax_errors_preserve_item_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root / "CAP-001.md",
                """
                ---
                id: CAP-001
                type: capability
                relations:
                  requires:
                    - not-an-entity-id
                ---

                # Capability
                """,
            )

            index = build_repository_index(load_repository(root))
            diagnostic = next(item for item in index.diagnostics if item.code == "reference.syntax")

            self.assertEqual(diagnostic.line, 6)
            self.assertEqual(diagnostic.address, "CAP-001")
            self.assertFalse(index.references)

    def test_dplus_reference_format_errors_are_not_duplicated_by_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_relationship_document(root, "CAP-001.md", "CAP-001", "invalid")

            repository = load_repository(root)
            index = build_repository_index(repository)

            self.assertIn("reference.format", [item.code for item in repository.diagnostics])
            self.assertNotIn("reference.syntax", [item.code for item in index.diagnostics])
            self.assertFalse(index.references)

    def test_reference_serialization_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_entity(root, "target.md", "CAP-001", "capability")
            self._write_relationship_document(root, "z.md", "CAP-003", "CAP-001")
            self._write_relationship_document(root, "a.md", "CAP-002", "CAP-001")

            first = build_repository_index(load_repository(root)).to_dict()
            second = build_repository_index(load_repository(root)).to_dict()

            self.assertEqual(first, second)
            self.assertEqual([item["path"] for item in first["references"]], ["a.md", "z.md"])
            json.dumps(first)

    def test_resolves_all_current_dogfood_references(self) -> None:
        index = build_repository_index(load_repository(REPO_ROOT / "model"))

        self.assertEqual(len(index.references), 79)
        self.assertTrue(all(item.resolution == ReferenceResolution.RESOLVED for item in index.references))
        self.assertEqual(len(index.capability_parents), 7)
        self.assertFalse(index.has_errors, index.diagnostics)


class RepositoryGraphValidationTests(unittest.TestCase):
    def _write_manifest(self, root: Path, core: str | None = "CAP-001", path: str = "product.yaml") -> None:
        core_line = f"coreCapability: {core}\n" if core is not None else ""
        write(
            root / path,
            f"formatVersion: \"0.1\"\n"
            f"id: PROD-{1 if path == 'product.yaml' else 2:03d}\n"
            f"type: product\n"
            f"title: Example\n"
            f"{core_line}",
        )

    def _write_entity(
        self,
        root: Path,
        path: str,
        entity_id: str,
        entity_type: str,
        lines: tuple[str, ...] = (),
    ) -> None:
        metadata = "\n".join(lines)
        extra = f"{metadata}\n" if metadata else ""
        write(
            root / path,
            f"---\n"
            f"id: {entity_id}\n"
            f"type: {entity_type}\n"
            f"{extra}"
            f"---\n\n"
            f"# {entity_id}\n",
        )

    def _validate(self, root: Path):
        repository = load_repository(root)
        index = build_repository_index(repository)
        return repository, index, validate_repository_graph(repository, index)

    def test_requires_exactly_one_product_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, missing = self._validate(root)
            self.assertEqual([item.code for item in missing.diagnostics], ["product.manifest-count"])

            self._write_manifest(root)
            self._write_manifest(root, path="nested/product.yml")
            _, _, multiple = self._validate(root)

            diagnostics = [item for item in multiple.diagnostics if item.code == "product.manifest-count"]
            self.assertEqual([item.path for item in diagnostics], ["nested/product.yml", "product.yaml"])
            self.assertIsNone(multiple.product_manifest)

    def test_requires_a_valid_core_capability_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root, core=None)

            _, _, validation = self._validate(root)

            self.assertEqual(validation.product_manifest, "product.yaml")
            self.assertIsNone(validation.core_capability)
            self.assertIn("product.core-capability-required", [item.code for item in validation.diagnostics])

    def test_detects_capability_cycles_and_disconnected_branches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: null",))
            self._write_entity(root, "CAP-002.md", "CAP-002", "capability", ("parent: CAP-003",))
            self._write_entity(root, "CAP-003.md", "CAP-003", "capability", ("parent: CAP-002",))
            self._write_entity(root, "CAP-004.md", "CAP-004", "capability", ("parent: CAP-002",))
            self._write_entity(root, "CAP-005.md", "CAP-005", "capability", ("parent: null",))

            _, _, validation = self._validate(root)

            self.assertEqual(validation.capability_cycles, (("CAP-002", "CAP-003", "CAP-002"),))
            cycle_diagnostics = [item for item in validation.diagnostics if item.code == "capability.cycle"]
            disconnected = [item for item in validation.diagnostics if item.code == "capability.disconnected"]
            self.assertEqual({item.address for item in cycle_diagnostics}, {"CAP-002", "CAP-003"})
            self.assertEqual({item.address for item in disconnected}, {"CAP-004", "CAP-005"})
            self.assertTrue(validation.has_errors)

    def test_detects_cycle_that_includes_core_capability(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: CAP-002",))
            self._write_entity(root, "CAP-002.md", "CAP-002", "capability", ("parent: CAP-001",))

            _, index, validation = self._validate(root)

            self.assertNotIn("CAP-001", index.capability_parents)
            self.assertEqual(validation.capability_cycles, (("CAP-001", "CAP-002", "CAP-001"),))
            self.assertEqual(
                {item.address for item in validation.diagnostics if item.code == "capability.cycle"},
                {"CAP-001", "CAP-002"},
            )

    def test_detects_self_parent_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: null",))
            self._write_entity(root, "CAP-002.md", "CAP-002", "capability", ("parent: CAP-002",))

            _, _, validation = self._validate(root)

            self.assertEqual(validation.capability_cycles, (("CAP-002", "CAP-002"),))

    def test_dependency_cycles_are_deterministic_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: null",))
            self._write_entity(
                root,
                "SUB-001.md",
                "SUB-001",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-002"),
            )
            self._write_entity(
                root,
                "SUB-002.md",
                "SUB-002",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-001"),
            )

            _, _, validation = self._validate(root)

            self.assertEqual(validation.dependency_cycles, (("SUB-001", "SUB-002", "SUB-001"),))
            diagnostics = [item for item in validation.diagnostics if item.code == "dependency.cycle"]
            self.assertEqual(len(diagnostics), 2)
            self.assertTrue(all(item.severity == "warning" for item in diagnostics))
            self.assertFalse(validation.has_errors)

    def test_dependency_scc_reports_each_distinct_cycle_and_matching_edge_messages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: null",))
            self._write_entity(
                root,
                "SUB-001.md",
                "SUB-001",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-002"),
            )
            self._write_entity(
                root,
                "SUB-002.md",
                "SUB-002",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-001", "    - SUB-003"),
            )
            self._write_entity(
                root,
                "SUB-003.md",
                "SUB-003",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-002"),
            )

            _, _, validation = self._validate(root)

            self.assertEqual(
                validation.dependency_cycles,
                (
                    ("SUB-001", "SUB-002", "SUB-001"),
                    ("SUB-002", "SUB-003", "SUB-002"),
                ),
            )
            sub3_diagnostic = next(
                item
                for item in validation.diagnostics
                if item.code == "dependency.cycle" and item.address == "SUB-003"
            )
            self.assertIn("SUB-003", sub3_diagnostic.message)

    def test_deep_acyclic_graph_algorithms_do_not_recurse(self) -> None:
        parents = {f"CAP-{index}": f"CAP-{index + 1}" for index in range(1500)}
        adjacency = {
            f"SUB-{index}": (f"SUB-{index + 1}",)
            for index in range(1500)
        }

        self.assertEqual(_functional_graph_cycles(parents), ())
        self.assertIsNone(_dependency_cycle_for_edge("SUB-0", "SUB-1", adjacency))

    def test_detects_dependency_self_cycle_but_not_acyclic_edges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: null",))
            self._write_entity(
                root,
                "SUB-001.md",
                "SUB-001",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-001", "    - SUB-002"),
            )
            self._write_entity(root, "SUB-002.md", "SUB-002", "subsystem")

            _, _, validation = self._validate(root)

            self.assertEqual(validation.dependency_cycles, (("SUB-001", "SUB-001"),))
            diagnostics = [item for item in validation.diagnostics if item.code == "dependency.cycle"]
            self.assertEqual(len(diagnostics), 1)
            self.assertEqual(diagnostics[0].address, "SUB-001")

    def test_validate_cli_includes_graph_validation_and_warning_exit_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write_entity(root, "CAP-001.md", "CAP-001", "capability", ("parent: null",))
            self._write_entity(
                root,
                "SUB-001.md",
                "SUB-001",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-002"),
            )
            self._write_entity(
                root,
                "SUB-002.md",
                "SUB-002",
                "subsystem",
                ("relations:", "  requires:", "    - SUB-001"),
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(["validate", str(root)])

            self.assertEqual(status, 0)
            self.assertIn("1 dependency cycles", stdout.getvalue())
            self.assertIn("dependency.cycle", stderr.getvalue())

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                json_status = main(["validate", str(root), "--json"])

            self.assertEqual(json_status, 0)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                payload["graphValidation"]["dependencyCycles"],
                [["SUB-001", "SUB-002", "SUB-001"]],
            )
            self.assertFalse(payload["hasErrors"])

    def test_current_dogfood_graph_is_valid_and_acyclic(self) -> None:
        repository = load_repository(REPO_ROOT / "model")
        index = build_repository_index(repository)
        validation = validate_repository_graph(repository, index)

        self.assertEqual(validation.product_manifest, "product.yaml")
        self.assertEqual(validation.core_capability, "CAP-001")
        self.assertEqual(validation.capability_cycles, ())
        self.assertEqual(validation.dependency_cycles, ())
        self.assertFalse(validation.has_errors, validation.diagnostics)


if __name__ == "__main__":
    unittest.main()
