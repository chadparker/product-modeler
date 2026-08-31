from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import DPlusError, parse_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse and validate Product Model D+ documents")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", help="print parsed documents as JSON")
    parser.add_argument(
        "--digests",
        action="store_true",
        help="print computed Claim content digests",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    failed = False
    documents = []

    for path in args.files:
        try:
            document = parse_file(path)
        except (DPlusError, OSError) as exc:
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
