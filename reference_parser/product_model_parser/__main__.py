from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import DPlusError, parse_file
from .repository import (
    RepositoryDiagnostic,
    build_repository_index,
    load_repository,
    validate_repository_graph,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse and validate Product Model D+ documents",
        epilog="Use 'product-model-parse inspect MODEL_DIR' to classify a repository.",
    )
    parser.add_argument("files", nargs="+", type=Path)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print parsed documents as JSON")
    output_group.add_argument(
        "--digests",
        action="store_true",
        help="print computed Claim content digests",
    )
    return parser


def _print_repository_diagnostic(diagnostic: RepositoryDiagnostic) -> None:
    address = f" [{diagnostic.address}]" if diagnostic.address else ""
    print(
        f"{diagnostic.path}:{diagnostic.line}: {diagnostic.severity}: "
        f"{diagnostic.code}{address}: {diagnostic.message}",
        file=sys.stderr,
    )


def _inspect(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="product-model-parse inspect",
        description="Discover and classify files in a Product Model repository",
    )
    parser.add_argument("directory", type=Path)
    parser.add_argument("--json", action="store_true", help="print repository classification as JSON")
    args = parser.parse_args(argv)

    try:
        repository = load_repository(args.directory)
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(repository.to_dict(), indent=2, sort_keys=True))
    else:
        counts = ", ".join(
            f"{count} {kind}" for kind, count in repository.counts.items() if count
        )
        print(f"{args.directory}: {len(repository.files)} files ({counts})")
        for item in repository.files:
            entity = f" [{item.entity_id}]" if item.entity_id else ""
            print(f"{item.kind.value:11} {item.path}{entity}")
        for diagnostic in repository.diagnostics:
            _print_repository_diagnostic(diagnostic)

    return 1 if repository.has_errors else 0


def _validate(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="product-model-parse validate",
        description="Validate identities in a Product Model repository",
    )
    parser.add_argument("directory", type=Path)
    parser.add_argument("--json", action="store_true", help="print validation results as JSON")
    args = parser.parse_args(argv)

    try:
        repository = load_repository(args.directory)
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 1

    index = build_repository_index(repository)
    graph_validation = validate_repository_graph(repository, index)
    diagnostics = sorted(
        [*repository.diagnostics, *index.diagnostics, *graph_validation.diagnostics],
        key=lambda item: (item.path, item.line, item.code, item.address or ""),
    )
    has_errors = any(item.severity == "error" for item in diagnostics)
    index_payload = index.to_dict()

    if args.json:
        payload = {
            **index_payload,
            "graphValidation": graph_validation.to_dict(),
            "repositoryCounts": repository.counts,
            "hasErrors": has_errors,
            "diagnostics": [item.to_dict() for item in diagnostics],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        counts = index_payload["counts"]
        print(
            f"{args.directory}: {counts['entityDeclarations']} entity declarations "
            f"({counts['uniqueEntities']} unique), {counts['claimDeclarations']} Claim declarations "
            f"({counts['uniqueClaims']} unique), {counts['references']} references, "
            f"{len(graph_validation.capability_cycles)} Capability cycles, "
            f"{len(graph_validation.dependency_cycles)} dependency cycles"
        )
        for diagnostic in diagnostics:
            _print_repository_diagnostic(diagnostic)

    return 1 if has_errors else 0


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "inspect" and len(arguments) > 1:
        return _inspect(arguments[1:])
    if arguments and arguments[0] == "validate":
        return _validate(arguments[1:])
    if arguments and arguments[0] == "parse":
        arguments = arguments[1:]

    args = _build_parser().parse_args(arguments)
    failed = False
    documents = []

    for path in args.files:
        try:
            document = parse_file(path)
        except (DPlusError, OSError, UnicodeError) as exc:
            failed = True
            print(exc, file=sys.stderr)
            continue

        documents.append(document)
        for diagnostic in document.diagnostics:
            location = f"{path}:{diagnostic.line}" if diagnostic.line else str(path)
            address = f" [{diagnostic.address}]" if diagnostic.address else ""
            print(
                f"{location}: {diagnostic.severity}: {diagnostic.code}{address}: {diagnostic.message}",
                file=sys.stderr,
            )
            if diagnostic.severity == "error":
                failed = True

        if args.digests:
            for claim in document.claims:
                print(f"{document.id}#{claim.id} {claim.content_digest}")
        elif not args.json and document.valid:
            print(
                f"{path}: valid D+ document ({len(document.claims)} claims, "
                f"{len(document.relationships)} relationships)"
            )

    if args.json:
        payload = [document.to_dict() for document in documents]
        print(json.dumps(payload[0] if len(payload) == 1 else payload, indent=2, sort_keys=True))

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
