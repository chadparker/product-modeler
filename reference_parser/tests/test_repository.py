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
from product_model_parser.repository import FileKind, load_repository


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


if __name__ == "__main__":
    unittest.main()
