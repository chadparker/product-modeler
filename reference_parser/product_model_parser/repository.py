from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path, PurePosixPath
import re
from typing import Any

from .parser import (
    Claim,
    DPlusError,
    Document,
    ENTITY_ID_RE,
    parse_text,
    parse_yaml_mapping,
    yaml_mapping_key_lines,
    yaml_value_lines,
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


class ReferenceKind(str, Enum):
    CORE_CAPABILITY = "core-capability"
    PARENT = "parent"
    RELATIONSHIP = "relationship"
    PROVENANCE = "provenance"
    SOURCE = "source"


class ReferenceResolution(str, Enum):
    RESOLVED = "resolved"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"


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
    entity_line: int | None = None
    metadata_value_lines: dict[str, int] = field(default_factory=dict)

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
        if self.entity_line is not None:
            result["entityLine"] = self.entity_line
        if self.metadata_value_lines:
            result["metadataValueLines"] = self.metadata_value_lines
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


@dataclass(frozen=True)
class EntityDeclaration:
    entity_id: str
    entity_type: str | None
    path: str
    line: int
    kind: FileKind
    repository_file: RepositoryFile = field(repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.entity_id,
            "path": self.path,
            "line": self.line,
            "kind": self.kind.value,
        }
        if self.entity_type is not None:
            result["type"] = self.entity_type
        return result


@dataclass(frozen=True)
class ClaimDeclaration:
    address: str
    entity_id: str
    local_id: str
    path: str
    line: int
    claim: Claim = field(repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "entityId": self.entity_id,
            "localId": self.local_id,
            "path": self.path,
            "line": self.line,
        }


@dataclass(frozen=True)
class ReferenceDeclaration:
    kind: ReferenceKind
    source_address: str
    source_entity_id: str
    target_id: str
    path: str
    line: int
    resolution: ReferenceResolution
    relationship_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "kind": self.kind.value,
            "source": self.source_address,
            "sourceEntityId": self.source_entity_id,
            "target": self.target_id,
            "path": self.path,
            "line": self.line,
            "resolution": self.resolution.value,
        }
        if self.relationship_type is not None:
            result["relationshipType"] = self.relationship_type
        return result


@dataclass
class RepositoryIndex:
    root: Path
    entity_declarations: dict[str, tuple[EntityDeclaration, ...]]
    claim_declarations: dict[str, tuple[ClaimDeclaration, ...]]
    entities_by_id: dict[str, EntityDeclaration]
    claims_by_address: dict[str, ClaimDeclaration]
    entities_by_file: dict[str, EntityDeclaration]
    references: tuple[ReferenceDeclaration, ...] = ()
    outgoing_references: dict[str, tuple[ReferenceDeclaration, ...]] = field(default_factory=dict)
    incoming_references: dict[str, tuple[ReferenceDeclaration, ...]] = field(default_factory=dict)
    capability_parents: dict[str, str] = field(default_factory=dict)
    capability_children: dict[str, tuple[str, ...]] = field(default_factory=dict)
    diagnostics: list[RepositoryDiagnostic] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(item.severity == "error" for item in self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "counts": {
                "entityDeclarations": sum(len(items) for items in self.entity_declarations.values()),
                "uniqueEntities": len(self.entities_by_id),
                "claimDeclarations": sum(len(items) for items in self.claim_declarations.values()),
                "uniqueClaims": len(self.claims_by_address),
                "references": len(self.references),
            },
            "hasErrors": self.has_errors,
            "entities": [
                declaration.to_dict()
                for entity_id in sorted(self.entity_declarations)
                for declaration in self.entity_declarations[entity_id]
            ],
            "claims": [
                declaration.to_dict()
                for address in sorted(self.claim_declarations)
                for declaration in self.claim_declarations[address]
            ],
            "references": [item.to_dict() for item in self.references],
            "capabilityParents": self.capability_parents,
            "capabilityChildren": {
                entity_id: list(children)
                for entity_id, children in self.capability_children.items()
            },
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }


@dataclass
class GraphValidation:
    root: Path
    product_manifest: str | None
    core_capability: str | None
    capability_cycles: tuple[tuple[str, ...], ...]
    dependency_cycles: tuple[tuple[str, ...], ...]
    diagnostics: list[RepositoryDiagnostic] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(item.severity == "error" for item in self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "productManifest": self.product_manifest,
            "coreCapability": self.core_capability,
            "capabilityCycles": [list(cycle) for cycle in self.capability_cycles],
            "dependencyCycles": [list(cycle) for cycle in self.dependency_cycles],
            "hasErrors": self.has_errors,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }


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


def _metadata_has_entity_identity(metadata: dict[str, Any]) -> bool:
    entity_id = metadata.get("id")
    entity_type = metadata.get("type")
    return (
        bool(isinstance(entity_id, str) and ENTITY_ID_RE.fullmatch(entity_id))
        or entity_type in MODEL_ENTITY_TYPES
        or entity_type == "product"
    )


def _metadata_looks_like_model(metadata: dict[str, Any]) -> bool:
    has_identity_key = "id" in metadata or "type" in metadata
    return _metadata_has_entity_identity(metadata) or (
        metadata.get("formatVersion") == "0.1" and has_identity_key
    )


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

    raw_model_candidate = filename_implies_entity or _looks_like_model_metadata(frontmatter_text)
    if not terminated:
        if not raw_model_candidate:
            return RepositoryFile(relative_path, FileKind.SUPPORT)
        error = DPlusError("unterminated YAML frontmatter", source=str(path), line=1)
        return RepositoryFile(
            relative_path,
            FileKind.INVALID,
            diagnostics=[_parser_error(relative_path, error)],
        )
    try:
        metadata = parse_yaml_mapping(frontmatter_text, source=str(path), line=2)
    except DPlusError as exc:
        if not raw_model_candidate:
            return RepositoryFile(relative_path, FileKind.SUPPORT)
        return RepositoryFile(
            relative_path,
            FileKind.INVALID,
            diagnostics=[_parser_error(relative_path, exc)],
        )
    if not filename_implies_entity and not _metadata_looks_like_model(metadata):
        return RepositoryFile(relative_path, FileKind.SUPPORT, metadata=metadata)

    format_version = metadata.get("formatVersion")
    metadata_id = metadata.get("id")
    metadata_key_lines = yaml_mapping_key_lines(frontmatter_text, source=str(path), line=2)
    metadata_value_lines = yaml_value_lines(frontmatter_text, source=str(path), line=2)
    entity_line = (
        metadata_value_lines.get("id")
        if isinstance(metadata_id, str) and ENTITY_ID_RE.fullmatch(metadata_id)
        else None
    )
    if "formatVersion" in metadata and format_version != "0.1":
        address = metadata_id if entity_line is not None else None
        diagnostic = _diagnostic(
            relative_path,
            "format.unsupported",
            f"unsupported formatVersion {format_version!r}",
            line=metadata_key_lines.get("formatVersion", 2),
            address=address,
        )
        return RepositoryFile(
            relative_path,
            FileKind.UNSUPPORTED,
            metadata=metadata,
            diagnostics=[diagnostic],
            entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
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
                        address=metadata_id if entity_line is not None else None,
                    )
                ],
                entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
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
            entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
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
        if not has_entity_id:
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "legacy.id",
                    "legacy entity has an invalid or missing ID",
                    line=metadata_key_lines.get("id", 2),
                )
            )
        if not isinstance(entity_type, str) or not entity_type:
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "legacy.type",
                    "legacy entity has an invalid or missing type",
                    line=metadata_key_lines.get("type", 2),
                    address=entity_id if has_entity_id else None,
                )
            )
        if diagnostics:
            return RepositoryFile(
                relative_path,
                FileKind.INVALID,
                metadata=metadata,
                diagnostics=diagnostics,
                entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
            )
        diagnostics.append(
            _diagnostic(
                relative_path,
                "file.legacy",
                "legacy entity does not declare a D+ formatVersion",
                line=metadata_key_lines.get("formatVersion", 2),
                severity="warning",
                address=entity_id,
            )
        )
        return RepositoryFile(
            relative_path,
            FileKind.LEGACY,
            metadata=metadata,
            diagnostics=diagnostics,
            entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
        )

    return RepositoryFile(relative_path, FileKind.SUPPORT, metadata=metadata)


def _classify_yaml(path: Path, relative_path: str) -> RepositoryFile:
    text, read_error = _read_text(path, relative_path)
    if read_error is not None or text is None:
        return RepositoryFile(relative_path, FileKind.INVALID, diagnostics=[read_error])
    if text.startswith("\ufeff"):
        diagnostic = _diagnostic(relative_path, "file.bom", "UTF-8 BOM is not allowed", line=1)
        return RepositoryFile(relative_path, FileKind.INVALID, diagnostics=[diagnostic])

    manifest_candidate = path.name.lower() in {"product.yaml", "product.yml"}
    raw_model_candidate = (
        manifest_candidate
        or bool(ENTITY_FILENAME_RE.match(path.stem))
        or _looks_like_entity_identity(text)
    )
    try:
        metadata = parse_yaml_mapping(text, source=str(path), line=1)
    except DPlusError as exc:
        if not raw_model_candidate:
            return RepositoryFile(relative_path, FileKind.SUPPORT)
        return RepositoryFile(
            relative_path,
            FileKind.INVALID,
            diagnostics=[
                _diagnostic(
                    relative_path,
                    "manifest.yaml",
                    str(exc).split(": ", 1)[-1],
                    line=exc.line or 1,
                )
            ],
        )
    if (
        not manifest_candidate
        and not ENTITY_FILENAME_RE.match(path.stem)
        and not _metadata_has_entity_identity(metadata)
    ):
        return RepositoryFile(relative_path, FileKind.SUPPORT, metadata=metadata)

    metadata_id = metadata.get("id")
    metadata_key_lines = yaml_mapping_key_lines(text, source=str(path), line=1)
    metadata_value_lines = yaml_value_lines(text, source=str(path), line=1)
    entity_line = (
        metadata_value_lines.get("id")
        if isinstance(metadata_id, str) and ENTITY_ID_RE.fullmatch(metadata_id)
        else None
    )
    if "formatVersion" in metadata and metadata.get("formatVersion") != "0.1":
        diagnostic = _diagnostic(
            relative_path,
            "format.unsupported",
            f"unsupported formatVersion {metadata.get('formatVersion')!r}",
            line=metadata_key_lines.get("formatVersion", 1),
            address=metadata_id if entity_line is not None else None,
        )
        return RepositoryFile(
            relative_path,
            FileKind.UNSUPPORTED,
            metadata=metadata,
            diagnostics=[diagnostic],
            entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
        )

    if manifest_candidate:
        diagnostics: list[RepositoryDiagnostic] = []
        manifest_address = metadata_id if entity_line is not None else None
        if metadata.get("formatVersion") != "0.1":
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.format",
                    "product manifest requires formatVersion '0.1'",
                    line=metadata_key_lines.get("formatVersion", 1),
                    address=manifest_address,
                )
            )
        if metadata.get("type") != "product":
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.type",
                    "product manifest requires type 'product'",
                    line=metadata_key_lines.get("type", 1),
                    address=manifest_address,
                )
            )
        if entity_line is None:
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.id",
                    "product manifest has an invalid or missing ID",
                    line=metadata_key_lines.get("id", 1),
                    address=manifest_address,
                )
            )
        title = metadata.get("title")
        if not isinstance(title, str) or not title.strip():
            diagnostics.append(
                _diagnostic(
                    relative_path,
                    "manifest.title",
                    "product manifest has an invalid or missing title",
                    line=metadata_key_lines.get("title", 1),
                    address=manifest_address,
                )
            )
        kind = FileKind.MANIFEST if not diagnostics else FileKind.INVALID
        return RepositoryFile(
            relative_path,
            kind,
            metadata=metadata,
            diagnostics=diagnostics,
            entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
        )

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
            entity_line=entity_line,
            metadata_value_lines=metadata_value_lines,
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


def _metadata_value_line(item: RepositoryFile, path: str, fallback: int = 1) -> int:
    return item.metadata_value_lines.get(path, item.entity_line or fallback)


def _add_reference(
    references: list[ReferenceDeclaration],
    diagnostics: list[RepositoryDiagnostic],
    entity_declarations: dict[str, tuple[EntityDeclaration, ...]],
    *,
    kind: ReferenceKind,
    source_address: str,
    source_entity_id: str,
    target: Any,
    path: str,
    line: int,
    relationship_type: str | None = None,
    report_invalid: bool = True,
    expected_type: str | None = None,
    type_code: str = "reference.type",
) -> ReferenceDeclaration | None:
    if not isinstance(target, str) or not ENTITY_ID_RE.fullmatch(target):
        if report_invalid:
            diagnostics.append(
                _diagnostic(
                    path,
                    "reference.syntax",
                    f"{kind.value} target must be an entity ID matching {ENTITY_ID_RE.pattern}",
                    line=line,
                    address=source_address,
                )
            )
        return None

    targets = entity_declarations.get(target, ())
    if not targets:
        resolution = ReferenceResolution.MISSING
        diagnostics.append(
            _diagnostic(
                path,
                "reference.missing",
                f"{kind.value} target {target} does not exist",
                line=line,
                address=source_address,
            )
        )
    elif len(targets) > 1:
        resolution = ReferenceResolution.AMBIGUOUS
        locations = ", ".join(f"{item.path}:{item.line}" for item in targets)
        diagnostics.append(
            _diagnostic(
                path,
                "reference.ambiguous",
                f"{kind.value} target {target} is ambiguous; declared at {locations}",
                line=line,
                address=source_address,
            )
        )
    elif targets[0].kind in {FileKind.INVALID, FileKind.UNSUPPORTED}:
        resolution = ReferenceResolution.UNAVAILABLE
        diagnostics.append(
            _diagnostic(
                path,
                "reference.unavailable",
                f"{kind.value} target {target} is declared by an unusable {targets[0].kind.value} file "
                f"at {targets[0].path}:{targets[0].line}",
                line=line,
                address=source_address,
            )
        )
    else:
        resolution = ReferenceResolution.RESOLVED
        if expected_type is not None and targets[0].entity_type != expected_type:
            diagnostics.append(
                _diagnostic(
                    path,
                    type_code,
                    f"{kind.value} target {target} must have type {expected_type!r}, "
                    f"not {targets[0].entity_type!r}",
                    line=line,
                    address=source_address,
                )
            )

    declaration = ReferenceDeclaration(
        kind=kind,
        source_address=source_address,
        source_entity_id=source_entity_id,
        target_id=target,
        path=path,
        line=line,
        resolution=resolution,
        relationship_type=relationship_type,
    )
    references.append(declaration)
    return declaration


def _duplicate_diagnostics(
    code: str,
    identity_label: str,
    declarations: dict[str, tuple[EntityDeclaration, ...]] | dict[str, tuple[ClaimDeclaration, ...]],
    *,
    across_files_only: bool = False,
) -> list[RepositoryDiagnostic]:
    diagnostics: list[RepositoryDiagnostic] = []
    for identity in sorted(declarations):
        conflicts = declarations[identity]
        if len(conflicts) < 2 or (
            across_files_only and len({item.path for item in conflicts}) < 2
        ):
            continue
        for declaration in conflicts:
            others = [
                f"{other.path}:{other.line}"
                for other in conflicts
                if other is not declaration
            ]
            diagnostics.append(
                _diagnostic(
                    declaration.path,
                    code,
                    f"duplicate {identity_label} {identity}; also declared at {', '.join(others)}",
                    line=declaration.line,
                    address=identity,
                )
            )
    return diagnostics


def build_repository_index(repository: Repository) -> RepositoryIndex:
    entity_buckets: dict[str, list[EntityDeclaration]] = {}
    claim_buckets: dict[str, list[ClaimDeclaration]] = {}
    entities_by_file: dict[str, EntityDeclaration] = {}

    for item in repository.files:
        entity_id = item.entity_id
        if (
            item.kind != FileKind.SUPPORT
            and entity_id is not None
            and ENTITY_ID_RE.fullmatch(entity_id)
        ):
            entity_type_value = item.metadata.get("type")
            declaration = EntityDeclaration(
                entity_id=entity_id,
                entity_type=entity_type_value if isinstance(entity_type_value, str) else None,
                path=item.path,
                line=item.entity_line or 1,
                kind=item.kind,
                repository_file=item,
            )
            entity_buckets.setdefault(entity_id, []).append(declaration)
            entities_by_file[item.path] = declaration

        if item.document is None:
            continue
        for claim in item.document.claims:
            address = f"{item.document.id}#{claim.id}"
            declaration = ClaimDeclaration(
                address=address,
                entity_id=item.document.id,
                local_id=claim.id,
                path=item.path,
                line=claim.line,
                claim=claim,
            )
            claim_buckets.setdefault(address, []).append(declaration)

    entity_declarations = {
        entity_id: tuple(sorted(items, key=lambda item: (item.path, item.line)))
        for entity_id, items in sorted(entity_buckets.items())
    }
    claim_declarations = {
        address: tuple(sorted(items, key=lambda item: (item.path, item.line)))
        for address, items in sorted(claim_buckets.items())
    }
    entities_by_id = {
        entity_id: items[0]
        for entity_id, items in entity_declarations.items()
        if len(items) == 1
    }
    claims_by_address = {
        address: items[0]
        for address, items in claim_declarations.items()
        if len(items) == 1
    }

    references: list[ReferenceDeclaration] = []
    reference_diagnostics: list[RepositoryDiagnostic] = []
    core_capability_ids = {
        value
        for item in repository.files
        if item.kind != FileKind.SUPPORT and item.metadata.get("type") == "product"
        for value in [item.metadata.get("coreCapability")]
        if isinstance(value, str) and ENTITY_ID_RE.fullmatch(value)
    }

    for item in repository.files:
        source_entity_id = item.entity_id
        if (
            item.kind == FileKind.SUPPORT
            or source_entity_id is None
            or not ENTITY_ID_RE.fullmatch(source_entity_id)
        ):
            continue
        source_address = source_entity_id
        metadata = item.metadata
        entity_type = metadata.get("type")

        if entity_type == "product" and "coreCapability" in metadata:
            _add_reference(
                references,
                reference_diagnostics,
                entity_declarations,
                kind=ReferenceKind.CORE_CAPABILITY,
                source_address=source_address,
                source_entity_id=source_entity_id,
                target=metadata.get("coreCapability"),
                path=item.path,
                line=_metadata_value_line(item, "coreCapability"),
                expected_type="capability",
                type_code="product.core-capability-type",
            )

        if entity_type == "capability":
            parent_present = "parent" in metadata
            parent = metadata.get("parent")
            is_core = source_entity_id in core_capability_ids
            if is_core and parent not in (None, ""):
                reference_diagnostics.append(
                    _diagnostic(
                        item.path,
                        "capability.parent-root",
                        "the Core Capability must not declare a parent",
                        line=_metadata_value_line(item, "parent"),
                        address=source_address,
                    )
                )
            elif core_capability_ids and not is_core and (not parent_present or parent is None):
                reference_diagnostics.append(
                    _diagnostic(
                        item.path,
                        "capability.parent-required",
                        "non-core Capability must declare a parent",
                        line=_metadata_value_line(item, "parent"),
                        address=source_address,
                    )
                )
            if parent_present and parent is not None:
                _add_reference(
                    references,
                    reference_diagnostics,
                    entity_declarations,
                    kind=ReferenceKind.PARENT,
                    source_address=source_address,
                    source_entity_id=source_entity_id,
                    target=parent,
                    path=item.path,
                    line=_metadata_value_line(item, "parent"),
                    report_invalid=item.document is None,
                    expected_type="capability",
                    type_code="capability.parent-type",
                )

        if item.document is not None:
            for claim in item.document.claims:
                claim_address = f"{source_entity_id}#{claim.id}"
                for target in claim.effective_based_on:
                    _add_reference(
                        references,
                        reference_diagnostics,
                        entity_declarations,
                        kind=ReferenceKind.PROVENANCE,
                        source_address=claim_address,
                        source_entity_id=source_entity_id,
                        target=target,
                        path=item.path,
                        line=claim.line,
                        report_invalid=False,
                    )
            for relationship in item.document.relationships:
                relationship_address = f"{source_entity_id}#{relationship.id}"
                _add_reference(
                    references,
                    reference_diagnostics,
                    entity_declarations,
                    kind=ReferenceKind.RELATIONSHIP,
                    source_address=relationship_address,
                    source_entity_id=source_entity_id,
                    target=relationship.target,
                    path=item.path,
                    line=relationship.line,
                    relationship_type=relationship.type,
                    report_invalid=False,
                )
                for target in relationship.effective_based_on:
                    _add_reference(
                        references,
                        reference_diagnostics,
                        entity_declarations,
                        kind=ReferenceKind.PROVENANCE,
                        source_address=relationship_address,
                        source_entity_id=source_entity_id,
                        target=target,
                        path=item.path,
                        line=relationship.line,
                        report_invalid=False,
                    )
            continue

        if "sources" in metadata:
            sources = metadata.get("sources")
            if isinstance(sources, list):
                for index, target in enumerate(sources):
                    _add_reference(
                        references,
                        reference_diagnostics,
                        entity_declarations,
                        kind=ReferenceKind.SOURCE,
                        source_address=source_address,
                        source_entity_id=source_entity_id,
                        target=target,
                        path=item.path,
                        line=_metadata_value_line(item, f"sources[{index}]"),
                        expected_type="source",
                    )
            else:
                reference_diagnostics.append(
                    _diagnostic(
                        item.path,
                        "reference.structure",
                        "sources must be a list of entity IDs",
                        line=_metadata_value_line(item, "sources"),
                        address=source_address,
                    )
                )

        provenance = metadata.get("provenance")
        if "provenance" in metadata and not isinstance(provenance, list):
            reference_diagnostics.append(
                _diagnostic(
                    item.path,
                    "reference.structure",
                    "legacy provenance must be a list of mappings containing source",
                    line=_metadata_value_line(item, "provenance"),
                    address=source_address,
                )
            )
        elif isinstance(provenance, list):
            for index, entry in enumerate(provenance):
                if not isinstance(entry, dict) or "source" not in entry:
                    reference_diagnostics.append(
                        _diagnostic(
                            item.path,
                            "reference.structure",
                            "legacy provenance entry must be a mapping containing source",
                            line=_metadata_value_line(item, f"provenance[{index}]"),
                            address=source_address,
                        )
                    )
                    continue
                _add_reference(
                    references,
                    reference_diagnostics,
                    entity_declarations,
                    kind=ReferenceKind.PROVENANCE,
                    source_address=source_address,
                    source_entity_id=source_entity_id,
                    target=entry.get("source"),
                    path=item.path,
                    line=_metadata_value_line(item, f"provenance[{index}].source"),
                    expected_type="source",
                )

        relations = metadata.get("relations")
        if "relations" in metadata and not isinstance(relations, dict):
            reference_diagnostics.append(
                _diagnostic(
                    item.path,
                    "reference.structure",
                    "relations must be a mapping from relationship type to targets",
                    line=_metadata_value_line(item, "relations"),
                    address=source_address,
                )
            )
        elif isinstance(relations, dict):
            for relationship_type, targets in relations.items():
                if not isinstance(relationship_type, str):
                    continue
                values = targets if isinstance(targets, list) else [targets]
                for index, target in enumerate(values):
                    suffix = f"[{index}]" if isinstance(targets, list) else ""
                    _add_reference(
                        references,
                        reference_diagnostics,
                        entity_declarations,
                        kind=ReferenceKind.RELATIONSHIP,
                        source_address=source_address,
                        source_entity_id=source_entity_id,
                        target=target,
                        path=item.path,
                        line=_metadata_value_line(item, f"relations.{relationship_type}{suffix}"),
                        relationship_type=relationship_type,
                    )

        if "resolvedBy" in metadata:
            _add_reference(
                references,
                reference_diagnostics,
                entity_declarations,
                kind=ReferenceKind.RELATIONSHIP,
                source_address=source_address,
                source_entity_id=source_entity_id,
                target=metadata.get("resolvedBy"),
                path=item.path,
                line=_metadata_value_line(item, "resolvedBy"),
                relationship_type="resolvedBy",
                expected_type="decision",
            )
        expected_types = {
            "resolves": "question",
            "capabilities": "capability",
        }
        for field_name in ("resolves", "related", "appliesTo", "capabilities"):
            if field_name not in metadata:
                continue
            targets = metadata.get(field_name)
            if not isinstance(targets, list):
                reference_diagnostics.append(
                    _diagnostic(
                        item.path,
                        "reference.structure",
                        f"{field_name} must be a list of entity IDs",
                        line=_metadata_value_line(item, field_name),
                        address=source_address,
                    )
                )
                continue
            for index, target in enumerate(targets):
                _add_reference(
                    references,
                    reference_diagnostics,
                    entity_declarations,
                    kind=ReferenceKind.RELATIONSHIP,
                    source_address=source_address,
                    source_entity_id=source_entity_id,
                    target=target,
                    path=item.path,
                    line=_metadata_value_line(item, f"{field_name}[{index}]"),
                    relationship_type=field_name,
                    expected_type=expected_types.get(field_name),
                )

    references.sort(
        key=lambda item: (
            item.path,
            item.line,
            item.source_address,
            item.kind.value,
            item.relationship_type or "",
            item.target_id,
        )
    )
    outgoing_buckets: dict[str, list[ReferenceDeclaration]] = {}
    incoming_buckets: dict[str, list[ReferenceDeclaration]] = {}
    for reference in references:
        outgoing_buckets.setdefault(reference.source_address, []).append(reference)
        incoming_buckets.setdefault(reference.target_id, []).append(reference)
    outgoing_references = {
        address: tuple(items) for address, items in sorted(outgoing_buckets.items())
    }
    incoming_references = {
        target: tuple(items) for target, items in sorted(incoming_buckets.items())
    }

    capability_parents: dict[str, str] = {}
    capability_children_buckets: dict[str, list[str]] = {}
    for reference in references:
        if (
            reference.kind != ReferenceKind.PARENT
            or reference.resolution != ReferenceResolution.RESOLVED
            or reference.source_entity_id not in entities_by_id
            or reference.source_entity_id in core_capability_ids
        ):
            continue
        target = entities_by_id.get(reference.target_id)
        source = entities_by_id[reference.source_entity_id]
        if target is None or target.entity_type != "capability" or source.entity_type != "capability":
            continue
        capability_parents[reference.source_entity_id] = reference.target_id
        capability_children_buckets.setdefault(reference.target_id, []).append(reference.source_entity_id)
    capability_parents = dict(sorted(capability_parents.items()))
    capability_children = {
        entity_id: tuple(sorted(children))
        for entity_id, children in sorted(capability_children_buckets.items())
    }

    diagnostics = _duplicate_diagnostics(
        "entity.duplicate",
        "entity ID",
        entity_declarations,
    )
    diagnostics.extend(
        _duplicate_diagnostics(
            "claim.duplicate",
            "Claim address",
            claim_declarations,
            across_files_only=True,
        )
    )
    diagnostics.extend(reference_diagnostics)
    diagnostics.sort(key=lambda item: (item.path, item.line, item.code, item.address or ""))

    return RepositoryIndex(
        root=repository.root,
        entity_declarations=entity_declarations,
        claim_declarations=claim_declarations,
        entities_by_id=entities_by_id,
        claims_by_address=claims_by_address,
        entities_by_file=dict(sorted(entities_by_file.items())),
        references=tuple(references),
        outgoing_references=outgoing_references,
        incoming_references=incoming_references,
        capability_parents=capability_parents,
        capability_children=capability_children,
        diagnostics=diagnostics,
    )


def _rotate_cycle(cycle: list[str]) -> tuple[str, ...]:
    nodes = cycle[:-1]
    start = min(range(len(nodes)), key=lambda index: nodes[index])
    rotated = nodes[start:] + nodes[:start]
    return tuple([*rotated, rotated[0]])


def _functional_graph_cycles(parents: dict[str, str]) -> tuple[tuple[str, ...], ...]:
    processed: set[str] = set()
    cycles: set[tuple[str, ...]] = set()

    for start in sorted(parents):
        if start in processed:
            continue
        path: list[str] = []
        positions: dict[str, int] = {}
        current = start
        while current in parents and current not in processed and current not in positions:
            positions[current] = len(path)
            path.append(current)
            current = parents[current]
        if current in positions:
            cycle = [*path[positions[current] :], current]
            cycles.add(_rotate_cycle(cycle))
        processed.update(path)
    return tuple(sorted(cycles))


def _dependency_cycle_for_edge(
    source: str,
    target: str,
    adjacency: dict[str, tuple[str, ...]],
) -> tuple[str, ...] | None:
    if source == target:
        return (source, source)

    queue: deque[str] = deque([target])
    predecessor: dict[str, str | None] = {target: None}
    while queue:
        node = queue.popleft()
        for next_node in adjacency.get(node, ()):
            if next_node in predecessor:
                continue
            predecessor[next_node] = node
            if next_node == source:
                path = [source]
                current: str | None = source
                while current is not None:
                    current = predecessor[current]
                    if current is not None:
                        path.append(current)
                path.reverse()
                return _rotate_cycle([source, *path])
            queue.append(next_node)
    return None


def validate_repository_graph(
    repository: Repository,
    index: RepositoryIndex,
) -> GraphValidation:
    diagnostics: list[RepositoryDiagnostic] = []
    manifest_candidates = [
        item
        for item in repository.files
        if PurePosixPath(item.path).name.lower() in {"product.yaml", "product.yml"}
    ]
    product_manifest: str | None = None
    core_capability: str | None = None

    if len(manifest_candidates) != 1:
        if not manifest_candidates:
            diagnostics.append(
                _diagnostic(
                    ".",
                    "product.manifest-count",
                    "repository must contain exactly one product.yaml or product.yml manifest; found 0",
                )
            )
        else:
            count = len(manifest_candidates)
            for item in manifest_candidates:
                diagnostics.append(
                    _diagnostic(
                        item.path,
                        "product.manifest-count",
                        f"repository must contain exactly one product manifest; found {count}",
                        line=item.entity_line or 1,
                        address=item.entity_id,
                    )
                )
    else:
        manifest = manifest_candidates[0]
        product_manifest = manifest.path
        core_value = manifest.metadata.get("coreCapability")
        if not isinstance(core_value, str) or not ENTITY_ID_RE.fullmatch(core_value):
            diagnostics.append(
                _diagnostic(
                    manifest.path,
                    "product.core-capability-required",
                    "product manifest must declare one valid coreCapability entity ID",
                    line=_metadata_value_line(manifest, "coreCapability"),
                    address=manifest.entity_id,
                )
            )
        else:
            core_reference = next(
                (
                    item
                    for item in index.outgoing_references.get(manifest.entity_id or "", ())
                    if item.kind == ReferenceKind.CORE_CAPABILITY
                    and item.target_id == core_value
                ),
                None,
            )
            target = index.entities_by_id.get(core_value)
            if (
                core_reference is not None
                and core_reference.resolution == ReferenceResolution.RESOLVED
                and target is not None
                and target.entity_type == "capability"
            ):
                core_capability = core_value

    cycle_parent_map: dict[str, str] = {}
    for reference in index.references:
        if (
            reference.kind != ReferenceKind.PARENT
            or reference.resolution != ReferenceResolution.RESOLVED
            or reference.source_entity_id not in index.entities_by_id
            or reference.target_id not in index.entities_by_id
            or index.entities_by_id[reference.source_entity_id].entity_type != "capability"
            or index.entities_by_id[reference.target_id].entity_type != "capability"
        ):
            continue
        cycle_parent_map[reference.source_entity_id] = reference.target_id
    capability_cycles = _functional_graph_cycles(cycle_parent_map)
    cycle_nodes = {node for cycle in capability_cycles for node in cycle[:-1]}
    for cycle in capability_cycles:
        description = " -> ".join(cycle)
        for entity_id in cycle[:-1]:
            reference = next(
                (
                    item
                    for item in index.outgoing_references.get(entity_id, ())
                    if item.kind == ReferenceKind.PARENT
                    and item.target_id == cycle_parent_map.get(entity_id)
                ),
                None,
            )
            declaration = index.entities_by_id[entity_id]
            diagnostics.append(
                _diagnostic(
                    reference.path if reference is not None else declaration.path,
                    "capability.cycle",
                    f"Capability parent cycle: {description}",
                    line=reference.line if reference is not None else declaration.line,
                    address=entity_id,
                )
            )

    if core_capability is not None:
        capabilities = sorted(
            entity_id
            for entity_id, declaration in index.entities_by_id.items()
            if declaration.entity_type == "capability" and entity_id != core_capability
        )
        for entity_id in capabilities:
            if entity_id in cycle_nodes:
                continue
            seen: set[str] = set()
            current = entity_id
            reaches_core = False
            while current not in seen:
                if current == core_capability:
                    reaches_core = True
                    break
                seen.add(current)
                parent = index.capability_parents.get(current)
                if parent is None:
                    break
                current = parent
            if reaches_core:
                continue
            declaration = index.entities_by_id[entity_id]
            reference = next(
                (
                    item
                    for item in index.outgoing_references.get(entity_id, ())
                    if item.kind == ReferenceKind.PARENT
                ),
                None,
            )
            diagnostics.append(
                _diagnostic(
                    reference.path if reference is not None else declaration.path,
                    "capability.disconnected",
                    f"Capability does not reach Core Capability {core_capability}",
                    line=reference.line if reference is not None else declaration.line,
                    address=entity_id,
                )
            )

    dependency_types = {"requires", "dependson", "depends-on"}
    dependency_references = [
        item
        for item in index.references
        if item.kind == ReferenceKind.RELATIONSHIP
        and item.resolution == ReferenceResolution.RESOLVED
        and isinstance(item.relationship_type, str)
        and item.relationship_type.lower() in dependency_types
        and item.source_entity_id in index.entities_by_id
        and item.target_id in index.entities_by_id
    ]
    adjacency_buckets: dict[str, set[str]] = {}
    for reference in dependency_references:
        adjacency_buckets.setdefault(reference.source_entity_id, set()).add(reference.target_id)
    adjacency = {
        source: tuple(sorted(targets))
        for source, targets in sorted(adjacency_buckets.items())
    }
    cycle_cache: dict[tuple[str, str], tuple[str, ...] | None] = {}
    dependency_cycle_set: set[tuple[str, ...]] = set()
    for reference in dependency_references:
        edge = (reference.source_entity_id, reference.target_id)
        if edge not in cycle_cache:
            cycle_cache[edge] = _dependency_cycle_for_edge(
                reference.source_entity_id,
                reference.target_id,
                adjacency,
            )
        cycle = cycle_cache[edge]
        if cycle is None:
            continue
        dependency_cycle_set.add(cycle)
        diagnostics.append(
            _diagnostic(
                reference.path,
                "dependency.cycle",
                f"dependency cycle: {' -> '.join(cycle)}",
                line=reference.line,
                severity="warning",
                address=reference.source_address,
            )
        )
    dependency_cycles = tuple(sorted(dependency_cycle_set))

    diagnostics.sort(key=lambda item: (item.path, item.line, item.code, item.address or ""))
    return GraphValidation(
        root=repository.root,
        product_manifest=product_manifest,
        core_capability=core_capability,
        capability_cycles=capability_cycles,
        dependency_cycles=dependency_cycles,
        diagnostics=diagnostics,
    )
