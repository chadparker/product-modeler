from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
from typing import Any

from .parser import (
    DPlusError,
    Document,
    ENTITY_ID_RE,
    parse_text,
    parse_yaml_mapping,
)


ENTITY_FILENAME_RE = re.compile(r"^[A-Z]+-[0-9]+(?:-|$)")
MODEL_ENTITY_TYPES = {
    "candidate",
    "capability",
    "constraint",
    "decision",
    "domain-concept",
    "interface",
    "journey",
    "observation",
    "question",
    "source",
    "subsystem",
}


class FileKind(str, Enum):
    DPLUS = "dplus"
    MANIFEST = "manifest"
    LEGACY = "legacy"
    SUPPORT = "support"
    UNSUPPORTED = "unsupported"
    INVALID = "invalid"


@dataclass(frozen=True)
class RepositoryDiagnostic:
    severity: str
    code: str
    message: str
    path: str
    line: int
    address: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "line": self.line,
        }
        if self.address is not None:
            result["address"] = self.address
        return result


@dataclass
class RepositoryFile:
    path: str
    kind: FileKind
    metadata: dict[str, Any] = field(default_factory=dict)
    document: Document | None = None
    diagnostics: list[RepositoryDiagnostic] = field(default_factory=list)

    @property
    def entity_id(self) -> str | None:
        value = self.metadata.get("id")
        return value if isinstance(value, str) else None

    @property
    def valid(self) -> bool:
        return not any(item.severity == "error" for item in self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "path": self.path,
            "kind": self.kind.value,
            "valid": self.valid,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        if self.document is not None:
            result["document"] = {
                "id": self.document.id,
                "type": self.document.type,
                "title": self.document.title,
                "claims": len(self.document.claims),
                "relationships": len(self.document.relationships),
            }
        if self.diagnostics:
            result["diagnostics"] = [item.to_dict() for item in self.diagnostics]
        return result


@dataclass
class Repository:
    root: Path
    files: list[RepositoryFile]

    @property
    def diagnostics(self) -> list[RepositoryDiagnostic]:
        return [diagnostic for item in self.files for diagnostic in item.diagnostics]

    @property
    def counts(self) -> dict[str, int]:
        observed = Counter(item.kind.value for item in self.files)
        return {kind.value: observed.get(kind.value, 0) for kind in FileKind}

    @property
    def has_errors(self) -> bool:
        return any(item.severity == "error" for item in self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "counts": self.counts,
            "hasErrors": self.has_errors,
            "files": [item.to_dict() for item in self.files],
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }


def _diagnostic(
    path: str,
    code: str,
    message: str,
    *,
    line: int = 1,
    severity: str = "error",
    address: str | None = None,
) -> RepositoryDiagnostic:
    return RepositoryDiagnostic(severity, code, message, path, line, address)


def _raw_top_level_value(text: str, key: str) -> str | None:
    pattern = re.compile(
        rf"^(?:{re.escape(key)}|['\"]{re.escape(key)}['\"])\s*:\s*([^#\n]*?)\s*(?:#.*)?$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'\"', "'"}:
        value = value[1:-1]
    return value


def _looks_like_entity_identity(text: str) -> bool:
    entity_id = _raw_top_level_value(text, "id")
    entity_type = _raw_top_level_value(text, "type")
    return (
        bool(entity_id and ENTITY_ID_RE.fullmatch(entity_id))
        or entity_type in MODEL_ENTITY_TYPES
        or entity_type == "product"
    )


def _looks_like_model_metadata(text: str) -> bool:
    format_version = _raw_top_level_value(text, "formatVersion")
    has_identity_key = (
        _raw_top_level_value(text, "id") is not None
        or _raw_top_level_value(text, "type") is not None
    )
    return _looks_like_entity_identity(text) or (format_version == "0.1" and has_identity_key)


def _top_level_key_line(text: str, key: str, *, start_line: int = 1) -> int:
    pattern = re.compile(rf"^(?:{re.escape(key)}|['\"]{re.escape(key)}['\"])\s*:")
    for offset, line in enumerate(text.splitlines()):
        if pattern.match(line):
            return start_line + offset
    return start_line


def _frontmatter_key_line(text: str, key: str) -> int:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return 1
    return _top_level_key_line("\n".join(lines[1:closing]), key, start_line=2)


def _read_text(path: Path, relative_path: str) -> tuple[str | None, RepositoryDiagnostic | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, _diagnostic(
            relative_path,
            "file.encoding",
            f"file is not valid UTF-8: {exc}",
            line=1,
        )
    except OSError as exc:
        return None, _diagnostic(
            relative_path,
            "file.read",
            str(exc),
            line=1,
        )


def _markdown_frontmatter_text(text: str) -> tuple[str | None, bool]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        return None, True
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return "\n".join(lines[1:]), False
    return "\n".join(lines[1:closing]), True


def _parser_error(
    path: str,
    error: DPlusError,
    *,
    address: str | None = None,
) -> RepositoryDiagnostic:
    return _diagnostic(
        path,
        "document.structure",
        str(error).split(": ", 1)[-1],
        line=error.line or 1,
        address=address,
    )


def _classify_markdown(path: Path, relative_path: str) -> RepositoryFile:
    text, read_error = _read_text(path, relative_path)
    if read_error is not None or text is None:
        return RepositoryFile(relative_path, FileKind.INVALID, diagnostics=[read_error])

    if text.startswith("\ufeff"):
        diagnostic = _diagnostic(relative_path, "file.bom", "UTF-8 BOM is not allowed", line=1)
        return RepositoryFile(relative_path, FileKind.INVALID, diagnostics=[diagnostic])

    frontmatter_text, terminated = _markdown_frontmatter_text(text)
    filename_implies_entity = bool(ENTITY_FILENAME_RE.match(path.stem))
    if frontmatter_text is None:
        if filename_implies_entity:
            error = DPlusError(
                "entity-named Markdown file must start with YAML frontmatter",
                source=str(path),
                line=1,
            )
            return RepositoryFile(
                relative_path,
                FileKind.INVALID,
                diagnostics=[_parser_error(relative_path, error)],
            )
        return RepositoryFile(relative_path, FileKind.SUPPORT)

    model_candidate = filename_implies_entity or _looks_like_model_metadata(frontmatter_text)
    if not model_candidate:
        return RepositoryFile(relative_path, FileKind.SUPPORT)
    if not terminated:
        error = DPlusError("unterminated YAML frontmatter", source=str(path), line=1)
        return RepositoryFile(
            relative_path,
            FileKind.INVALID,
            diagnostics=[_parser_error(relative_path, error)],
        )
    try:
        metadata = parse_yaml_mapping(frontmatter_text, source=str(path), line=2)
    except DPlusError as exc:
        return RepositoryFile(
            relative_path,
            FileKind.INVALID,
            diagnostics=[_parser_error(relative_path, exc)],
        )

    format_version = metadata.get("formatVersion")
    if "formatVersion" in metadata and format_version != "0.1":
        address = metadata.get("id") if isinstance(metadata.get("id"), str) and ENTITY_ID_RE.fullmatch(metadata["id"]) else None
        diagnostic = _diagnostic(
            relative_path,
            "format.unsupported",
            f"unsupported formatVersion {format_version!r}",
            line=_frontmatter_key_line(text, "formatVersion"),
            address=address,
        )
        return RepositoryFile(
            relative_path,
            FileKind.UNSUPPORTED,
            metadata=metadata,
            diagnostics=[diagnostic],
        )

    if format_version == "0.1":
        try:
            document = parse_text(text, source=str(path))
        except DPlusError as exc:
            return RepositoryFile(
                relative_path,
                FileKind.INVALID,
                metadata=metadata,
                diagnostics=[
                    _parser_error(
                        relative_path,
                        exc,
                        address=metadata["id"]
                        if isinstance(metadata.get("id"), str) and ENTITY_ID_RE.fullmatch(metadata["id"])
                        else None,
                    )
                ],
            )
        diagnostics = [
            RepositoryDiagnostic(
                item.severity,
                item.code,
                item.message,
                relative_path,
                item.line or 1,
                item.address,
            )
            for item in document.diagnostics
        ]
        return RepositoryFile(
            relative_path,
            FileKind.DPLUS,
            metadata=document.metadata,
            document=document,
            diagnostics=diagnostics,
        )

    entity_id = metadata.get("id")
    entity_type = metadata.get("type")
    has_entity_id = isinstance(entity_id, str) and bool(ENTITY_ID_RE.fullmatch(entity_id))
    legacy_candidate = (
        has_entity_id
        or entity_type in MODEL_ENTITY_TYPES
        or bool(ENTITY_FILENAME_RE.match(path.stem))
    )
    if legacy_candidate:
        diagnostics: list[RepositoryDiagnostic] = []
        if not isinstance(metadata.get("id"), str) or not ENTITY_ID_RE.fullmatch(metadata["id"]):
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "legacy.id",
                    "legacy entity has an invalid or missing ID",
                    line=_frontmatter_key_line(text, "id"),
                )
            )
        if not isinstance(metadata.get("type"), str) or not metadata["type"]:
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "legacy.type",
                    "legacy entity has an invalid or missing type",
                    line=_frontmatter_key_line(text, "type"),
                    address=entity_id if has_entity_id else None,
                )
            )
        if diagnostics:
            return RepositoryFile(relative_path, FileKind.INVALID, metadata=metadata, diagnostics=diagnostics)
        diagnostics.append(
            _diagnostic(
                relative_path,
                "file.legacy",
                "legacy entity does not declare a D+ formatVersion",
                line=_frontmatter_key_line(text, "formatVersion"),
                severity="warning",
                address=metadata["id"],
            )
        )
        return RepositoryFile(relative_path, FileKind.LEGACY, metadata=metadata, diagnostics=diagnostics)

    return RepositoryFile(relative_path, FileKind.SUPPORT, metadata=metadata)


def _classify_yaml(path: Path, relative_path: str) -> RepositoryFile:
    text, read_error = _read_text(path, relative_path)
    if read_error is not None or text is None:
        return RepositoryFile(relative_path, FileKind.INVALID, diagnostics=[read_error])
    if text.startswith("\ufeff"):
        diagnostic = _diagnostic(relative_path, "file.bom", "UTF-8 BOM is not allowed", line=1)
        return RepositoryFile(relative_path, FileKind.INVALID, diagnostics=[diagnostic])
    manifest_candidate = path.name.lower() in {"product.yaml", "product.yml"}
    model_candidate = (
        manifest_candidate
        or bool(ENTITY_FILENAME_RE.match(path.stem))
        or _looks_like_entity_identity(text)
    )
    if not model_candidate:
        return RepositoryFile(relative_path, FileKind.SUPPORT)
    try:
        metadata = parse_yaml_mapping(text, source=str(path), line=1)
    except DPlusError as exc:
        return RepositoryFile(
            relative_path,
            FileKind.INVALID,
            diagnostics=[_diagnostic(relative_path, "manifest.yaml", str(exc).split(": ", 1)[-1], line=exc.line or 1)],
        )

    if "formatVersion" in metadata and metadata.get("formatVersion") != "0.1":
        address = metadata.get("id") if isinstance(metadata.get("id"), str) and ENTITY_ID_RE.fullmatch(metadata["id"]) else None
        diagnostic = _diagnostic(
            relative_path,
            "format.unsupported",
            f"unsupported formatVersion {metadata.get('formatVersion')!r}",
            line=_top_level_key_line(text, "formatVersion"),
            address=address,
        )
        return RepositoryFile(
            relative_path,
            FileKind.UNSUPPORTED,
            metadata=metadata,
            diagnostics=[diagnostic],
        )

    if manifest_candidate:
        diagnostics: list[RepositoryDiagnostic] = []
        manifest_id = metadata.get("id")
        manifest_address = (
            manifest_id
            if isinstance(manifest_id, str) and ENTITY_ID_RE.fullmatch(manifest_id)
            else None
        )
        if metadata.get("formatVersion") != "0.1":
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.format",
                    "product manifest requires formatVersion '0.1'",
                    line=_top_level_key_line(text, "formatVersion"),
                    address=manifest_address,
                )
            )
        if metadata.get("type") != "product":
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.type",
                    "product manifest requires type 'product'",
                    line=_top_level_key_line(text, "type"),
                    address=manifest_address,
                )
            )
        if not isinstance(metadata.get("id"), str) or not ENTITY_ID_RE.fullmatch(metadata["id"]):
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.id",
                    "product manifest has an invalid or missing ID",
                    line=_top_level_key_line(text, "id"),
                    address=manifest_address,
                )
            )
        if not isinstance(metadata.get("title"), str) or not metadata["title"].strip():
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.title",
                    "product manifest has an invalid or missing title",
                    line=_top_level_key_line(text, "title"),
                    address=manifest_address,
                )
            )
        kind = FileKind.MANIFEST if not diagnostics else FileKind.INVALID
        return RepositoryFile(relative_path, kind, metadata=metadata, diagnostics=diagnostics)

    entity_id = metadata.get("id")
    has_entity_id = isinstance(entity_id, str) and bool(ENTITY_ID_RE.fullmatch(entity_id))
    if has_entity_id or ENTITY_FILENAME_RE.match(path.stem):
        diagnostic = _diagnostic(
            relative_path,
            "yaml.unsupported-entity",
            "YAML entity documents other than the product manifest are not supported",
            address=entity_id if has_entity_id else None,
        )
        return RepositoryFile(
            relative_path,
            FileKind.UNSUPPORTED,
            metadata=metadata,
            diagnostics=[diagnostic],
        )

    return RepositoryFile(relative_path, FileKind.SUPPORT, metadata=metadata)


def _classify_file(path: Path, relative_path: str) -> RepositoryFile:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return _classify_markdown(path, relative_path)
    if suffix in {".yaml", ".yml"}:
        return _classify_yaml(path, relative_path)
    return RepositoryFile(relative_path, FileKind.SUPPORT)


def load_repository(root: str | Path) -> Repository:
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(root_path)
    if not root_path.is_dir():
        raise NotADirectoryError(root_path)

    paths = sorted(
        (
            path
            for path in root_path.rglob("*")
            if path.is_file()
            and not path.is_symlink()
            and not any(part.startswith(".") for part in path.relative_to(root_path).parts)
        ),
        key=lambda path: path.relative_to(root_path).as_posix(),
    )
    files = [
        _classify_file(path, path.relative_to(root_path).as_posix())
        for path in paths
    ]
    return Repository(root_path, files)
