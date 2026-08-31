from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml
from yaml.composer import ComposerError
from yaml.constructor import ConstructorError
from yaml.events import AliasEvent
from yaml.loader import SafeLoader


ENTITY_ID_RE = re.compile(r"^[A-Z]+-[0-9]+$")
LOCAL_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*$")
HEADING_RE = re.compile(r"^( {0,3})(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
REVIEW_STATES = {"provisional", "confirmed", "questioned", "proposed"}
SECTION_ORDER = {"Context": 0, "Claims": 1, "Relationships": 2}
ALLOWED_YAML_TAGS = {
    "tag:yaml.org,2002:map",
    "tag:yaml.org,2002:seq",
    "tag:yaml.org,2002:str",
    "tag:yaml.org,2002:int",
    "tag:yaml.org,2002:float",
    "tag:yaml.org,2002:bool",
    "tag:yaml.org,2002:null",
}


class DPlusError(ValueError):
    def __init__(self, message: str, *, source: str = "<string>", line: int | None = None):
        self.source = source
        self.line = line
        location = f"{source}:{line}" if line is not None else source
        super().__init__(f"{location}: {message}")


class StrictLoader(SafeLoader):
    """Safe YAML loader that rejects aliases, anchors, merges, and duplicate keys."""

    def compose_node(self, parent: Any, index: Any) -> yaml.Node:
        event = self.peek_event()
        if isinstance(event, AliasEvent):
            raise ComposerError(None, None, "YAML aliases are not allowed", event.start_mark)
        if getattr(event, "anchor", None) is not None:
            raise ComposerError(None, None, "YAML anchors are not allowed", event.start_mark)
        if getattr(event, "tag", None) is not None:
            raise ComposerError(None, None, "explicit YAML tags are not allowed", event.start_mark)
        node = super().compose_node(parent, index)
        if node.tag not in ALLOWED_YAML_TAGS:
            raise ComposerError(None, None, f"YAML tag {node.tag!r} is not allowed", node.start_mark)
        return node

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        if not isinstance(node, yaml.MappingNode):
            raise ConstructorError(None, None, "expected a mapping", node.start_mark)
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise ConstructorError(None, None, "YAML merge keys are not allowed", key_node.start_mark)
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"duplicate key: {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


# PyYAML defaults to YAML 1.1 scalar resolution. D+ uses JSON-compatible
# implicit scalars so values such as yes, 012, 12:30, .inf, and dates remain
# strings rather than silently changing type.
_REMOVED_IMPLICIT_TAGS = {
    "tag:yaml.org,2002:bool",
    "tag:yaml.org,2002:int",
    "tag:yaml.org,2002:float",
    "tag:yaml.org,2002:null",
    "tag:yaml.org,2002:timestamp",
}
StrictLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in resolvers if tag not in _REMOVED_IMPLICIT_TAGS]
    for key, resolvers in SafeLoader.yaml_implicit_resolvers.items()
}
StrictLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$"),
    list("tf"),
)
StrictLoader.add_implicit_resolver(
    "tag:yaml.org,2002:null",
    re.compile(r"^null$"),
    ["n"],
)
StrictLoader.add_implicit_resolver(
    "tag:yaml.org,2002:int",
    re.compile(r"^-?(?:0|[1-9][0-9]*)$"),
    list("-0123456789"),
)
StrictLoader.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(
        r"^-?(?:(?:0|[1-9][0-9]*)\.[0-9]+(?:[eE][+-]?[0-9]+)?|"
        r"(?:0|[1-9][0-9]*)[eE][+-]?[0-9]+)$"
    ),
    list("-0123456789"),
)


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    line: int | None = None
    address: str | None = None


@dataclass
class Claim:
    id: str
    markdown: str
    metadata: dict[str, Any]
    line: int
    content_digest: str
    effective_review: dict[str, Any] = field(default_factory=dict)
    effective_based_on: list[str] = field(default_factory=list)

    @property
    def address(self) -> str:
        return self.id


@dataclass
class Relationship:
    id: str
    metadata: dict[str, Any]
    line: int
    effective_review: dict[str, Any] = field(default_factory=dict)
    effective_based_on: list[str] = field(default_factory=list)

    @property
    def type(self) -> str | None:
        value = self.metadata.get("type")
        return value if isinstance(value, str) else None

    @property
    def target(self) -> str | None:
        value = self.metadata.get("target")
        return value if isinstance(value, str) else None


@dataclass
class Document:
    source: str
    metadata: dict[str, Any]
    title: str
    context: str | None
    claims: list[Claim]
    relationships: list[Relationship]
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.metadata["id"])

    @property
    def valid(self) -> bool:
        return not any(item.severity == "error" for item in self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "metadata": self.metadata,
            "title": self.title,
            "context": self.context,
            "claims": [asdict(item) for item in self.claims],
            "relationships": [asdict(item) for item in self.relationships],
            "diagnostics": [asdict(item) for item in self.diagnostics],
            "valid": self.valid,
        }


@dataclass(frozen=True)
class Heading:
    line_index: int
    level: int
    text: str


@dataclass(frozen=True)
class Fence:
    start: int
    end: int
    info: str


@dataclass
class _OpenFence:
    char: str
    length: int
    info: str
    start: int


def _validate_yaml_shape(value: Any, *, source: str, line: int, path: str = "YAML") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise DPlusError(f"{path} mapping keys must be strings", source=source, line=line)
            _validate_yaml_shape(child, source=source, line=line, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_yaml_shape(child, source=source, line=line, path=f"{path}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise DPlusError(f"{path} contains a non-finite number", source=source, line=line)
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise DPlusError(f"{path} contains unsupported value type {type(value).__name__}", source=source, line=line)


def _yaml_mapping(text: str, *, source: str, line: int) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        value = yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
        error_line = line + mark.line if mark is not None else line
        raise DPlusError(f"invalid YAML: {exc}", source=source, line=error_line) from exc
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise DPlusError("YAML content must be a mapping", source=source, line=line)
    _validate_yaml_shape(value, source=source, line=line)
    return value


def _fence_open(line: str) -> tuple[str, int, str] | None:
    match = FENCE_RE.fullmatch(line)
    if not match:
        return None
    marker = match.group(2)
    info = match.group(3).strip()
    if marker[0] == "`" and "`" in info:
        return None
    return marker[0], len(marker), info


def _fence_close(line: str, opened: _OpenFence) -> bool:
    match = FENCE_RE.fullmatch(line)
    if not match:
        return False
    marker = match.group(2)
    info = match.group(3)
    return (
        marker[0] == opened.char
        and len(marker) >= opened.length
        and not info.strip()
    )


def _reserved_product_token(info: str) -> str | None:
    if not info:
        return None
    token = info.split(maxsplit=1)[0]
    return token if token.lower().startswith("product-") else None


def _scan_headings(lines: list[str], *, source: str, line_offset: int) -> list[Heading]:
    headings: list[Heading] = []
    opened: _OpenFence | None = None
    for index, line in enumerate(lines):
        if opened is not None:
            if _fence_close(line, opened):
                opened = None
            continue
        fence = _fence_open(line)
        if fence:
            opened = _OpenFence(fence[0], fence[1], fence[2], index)
            continue
        match = HEADING_RE.fullmatch(line)
        if match:
            raw_text = match.group(3) or ""
            text = re.sub(r"[ \t]+#+[ \t]*$", "", raw_text).strip()
            headings.append(Heading(index, len(match.group(2)), text))
    if opened is not None:
        raise DPlusError(
            "unterminated fenced block",
            source=source,
            line=line_offset + opened.start,
        )
    return headings


def _scan_fences(lines: list[str], *, source: str, line_offset: int) -> list[Fence]:
    fences: list[Fence] = []
    opened: _OpenFence | None = None
    for index, line in enumerate(lines):
        if opened is not None:
            if _fence_close(line, opened):
                fences.append(Fence(opened.start, index, opened.info))
                opened = None
            continue
        fence = _fence_open(line)
        if fence:
            opened = _OpenFence(fence[0], fence[1], fence[2], index)
    if opened is not None:
        raise DPlusError(
            "unterminated fenced block",
            source=source,
            line=line_offset + opened.start,
        )
    return fences


def normalize_claim_markdown(lines: list[str]) -> str:
    normalized = [line.rstrip(" \t") for line in lines]
    while normalized and not normalized[0]:
        normalized.pop(0)
    while normalized and not normalized[-1]:
        normalized.pop()
    return "\n".join(normalized)


def claim_digest(markdown: str) -> str:
    digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _extract_claim(
    local_id: str,
    block: list[str],
    *,
    source: str,
    heading_line: int,
) -> Claim:
    fences = _scan_fences(block, source=source, line_offset=heading_line + 1)
    unknown_reserved = [
        item
        for item in fences
        if _reserved_product_token(item.info) is not None
        and item.info not in {"product-claim", "product-relationship"}
    ]
    if unknown_reserved:
        raise DPlusError(
            f"unsupported reserved fence {unknown_reserved[0].info!r}",
            source=source,
            line=heading_line + 1 + unknown_reserved[0].start,
        )
    reserved = [item for item in fences if item.info in {"product-claim", "product-relationship"}]
    wrong = [item for item in reserved if item.info == "product-relationship"]
    if wrong:
        raise DPlusError(
            "product-relationship fence is not allowed inside a Claim",
            source=source,
            line=heading_line + 1 + wrong[0].start,
        )
    metadata_fences = [item for item in reserved if item.info == "product-claim"]
    if len(metadata_fences) > 1:
        raise DPlusError(
            "a Claim may contain at most one product-claim fence",
            source=source,
            line=heading_line,
        )

    metadata: dict[str, Any] = {}
    statement_lines = block
    if metadata_fences:
        fence = metadata_fences[0]
        if any(line.strip() for line in block[fence.end + 1 :]):
            raise DPlusError(
                "product-claim metadata must be the final nonblank content in its Claim",
                source=source,
                line=heading_line + 1 + fence.end,
            )
        metadata_text = "\n".join(block[fence.start + 1 : fence.end])
        metadata = _yaml_mapping(
            metadata_text,
            source=source,
            line=heading_line + 2 + fence.start,
        )
        statement_lines = block[: fence.start]

    markdown = normalize_claim_markdown(statement_lines)
    if not markdown:
        raise DPlusError("Claim content must not be empty", source=source, line=heading_line)
    return Claim(
        id=local_id,
        markdown=markdown,
        metadata=metadata,
        line=heading_line,
        content_digest=claim_digest(markdown),
    )


def _extract_relationship(
    local_id: str,
    block: list[str],
    *,
    source: str,
    heading_line: int,
) -> Relationship:
    fences = _scan_fences(block, source=source, line_offset=heading_line + 1)
    unknown_reserved = [
        item
        for item in fences
        if _reserved_product_token(item.info) is not None
        and item.info not in {"product-claim", "product-relationship"}
    ]
    if unknown_reserved:
        raise DPlusError(
            f"unsupported reserved fence {unknown_reserved[0].info!r}",
            source=source,
            line=heading_line + 1 + unknown_reserved[0].start,
        )
    metadata_fences = [item for item in fences if item.info == "product-relationship"]
    if len(metadata_fences) != 1:
        raise DPlusError(
            "a relationship must contain exactly one product-relationship fence",
            source=source,
            line=heading_line,
        )
    if any(item.info == "product-claim" for item in fences):
        raise DPlusError(
            "product-claim fence is not allowed inside a relationship",
            source=source,
            line=heading_line,
        )
    fence = metadata_fences[0]
    outside = block[: fence.start] + block[fence.end + 1 :]
    if any(line.strip() for line in outside):
        raise DPlusError(
            "a relationship may contain only its product-relationship fence",
            source=source,
            line=heading_line,
        )
    metadata_text = "\n".join(block[fence.start + 1 : fence.end])
    metadata = _yaml_mapping(
        metadata_text,
        source=source,
        line=heading_line + 2 + fence.start,
    )
    return Relationship(id=local_id, metadata=metadata, line=heading_line)


def _section_entries(
    lines: list[str],
    headings: list[Heading],
    *,
    section_start: int,
    section_end: int,
    source: str,
    line_offset: int,
    kind: str,
) -> list[Claim] | list[Relationship]:
    entries = [
        item
        for item in headings
        if item.level == 3 and section_start < item.line_index < section_end
    ]
    first_content = section_start + 1
    first_heading = entries[0].line_index if entries else section_end
    if any(line.strip() for line in lines[first_content:first_heading]):
        raise DPlusError(
            f"content in {kind} section must belong to a level-three entry",
            source=source,
            line=line_offset + first_content,
        )

    result: list[Claim] | list[Relationship] = []
    for position, heading in enumerate(entries):
        if not LOCAL_ID_RE.fullmatch(heading.text):
            raise DPlusError(
                f"invalid local ID {heading.text!r}; expected {LOCAL_ID_RE.pattern}",
                source=source,
                line=line_offset + heading.line_index,
            )
        end = entries[position + 1].line_index if position + 1 < len(entries) else section_end
        block = lines[heading.line_index + 1 : end]
        absolute_line = line_offset + heading.line_index
        if kind == "Claims":
            result.append(
                _extract_claim(
                    heading.text,
                    block,
                    source=source,
                    heading_line=absolute_line,
                )
            )
        else:
            result.append(
                _extract_relationship(
                    heading.text,
                    block,
                    source=source,
                    heading_line=absolute_line,
                )
            )
    return result


def _reject_reserved_fences(lines: list[str], *, source: str, line_offset: int, location: str) -> None:
    for fence in _scan_fences(lines, source=source, line_offset=line_offset):
        if _reserved_product_token(fence.info) is not None:
            raise DPlusError(
                f"reserved fence {fence.info!r} is not allowed in {location}",
                source=source,
                line=line_offset + fence.start,
            )


def _review_mapping(value: Any, *, address: str, diagnostics: list[Diagnostic], line: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        diagnostics.append(Diagnostic("error", "review.type", "review must be a mapping", line, address))
        return {}
    state = value.get("state")
    if "state" in value and state not in REVIEW_STATES:
        diagnostics.append(
            Diagnostic(
                "error",
                "review.state",
                f"unsupported review state {state!r}",
                line,
                address,
            )
        )
    return dict(value)


def _string_list(value: Any, *, field_name: str, address: str, diagnostics: list[Diagnostic], line: int) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        diagnostics.append(
            Diagnostic("error", "provenance.type", f"{field_name} must be a list of strings", line, address)
        )
        return []
    return list(value)


def _effective_based_on(
    defaults: list[str],
    metadata: dict[str, Any],
    *,
    address: str,
    diagnostics: list[Diagnostic],
    line: int,
) -> list[str]:
    if "provenance" not in metadata:
        return list(defaults)
    provenance = metadata["provenance"]
    if not isinstance(provenance, dict):
        diagnostics.append(Diagnostic("error", "provenance.type", "provenance must be a mapping", line, address))
        return list(defaults)
    if "basedOn" not in provenance:
        return list(defaults)
    based_on = provenance["basedOn"]
    if isinstance(based_on, list):
        return _string_list(
            based_on,
            field_name="provenance.basedOn",
            address=address,
            diagnostics=diagnostics,
            line=line,
        )
    if not isinstance(based_on, dict):
        diagnostics.append(
            Diagnostic(
                "error",
                "provenance.basedOn.type",
                "provenance.basedOn must be a list or an add/remove mapping",
                line,
                address,
            )
        )
        return list(defaults)
    unknown = set(based_on) - {"add", "remove"}
    if unknown:
        diagnostics.append(
            Diagnostic(
                "error",
                "provenance.basedOn.keys",
                f"unsupported provenance patch keys: {', '.join(sorted(unknown))}",
                line,
                address,
            )
        )
    remove = (
        _string_list(
            based_on["remove"],
            field_name="provenance.basedOn.remove",
            address=address,
            diagnostics=diagnostics,
            line=line,
        )
        if "remove" in based_on
        else []
    )
    add = (
        _string_list(
            based_on["add"],
            field_name="provenance.basedOn.add",
            address=address,
            diagnostics=diagnostics,
            line=line,
        )
        if "add" in based_on
        else []
    )
    for field_name, references in (("add", add), ("remove", remove)):
        for reference in references:
            _validate_reference(
                reference,
                field_name=f"provenance.basedOn.{field_name}",
                address=address,
                diagnostics=diagnostics,
                line=line,
            )
    result = [item for item in defaults if item not in set(remove)]
    for item in add:
        if item not in result:
            result.append(item)
    return result


def _valid_entity_reference(value: Any) -> bool:
    return isinstance(value, str) and bool(ENTITY_ID_RE.fullmatch(value))


def _validate_reference(
    value: Any,
    *,
    field_name: str,
    address: str,
    diagnostics: list[Diagnostic],
    line: int,
) -> None:
    if not _valid_entity_reference(value):
        diagnostics.append(
            Diagnostic(
                "error",
                "reference.format",
                f"{field_name} must be an entity ID matching {ENTITY_ID_RE.pattern}",
                line,
                address,
            )
        )


def _validate(document: Document) -> None:
    diagnostics = document.diagnostics
    if "parent" in document.metadata:
        _validate_reference(
            document.metadata["parent"],
            field_name="parent",
            address=document.id,
            diagnostics=diagnostics,
            line=1,
        )
    if "defaults" not in document.metadata:
        defaults: dict[str, Any] = {}
    elif not isinstance(document.metadata["defaults"], dict):
        diagnostics.append(Diagnostic("error", "defaults.type", "defaults must be a mapping"))
        defaults = {}
    else:
        defaults = document.metadata["defaults"]

    default_review = (
        _review_mapping(
            defaults["review"],
            address=document.id,
            diagnostics=diagnostics,
            line=1,
        )
        if "review" in defaults
        else {}
    )
    if "contentDigest" in default_review:
        diagnostics.append(
            Diagnostic(
                "error",
                "review.digest-default",
                "review.contentDigest cannot be inherited from entity defaults",
                1,
                document.id,
            )
        )
        default_review.pop("contentDigest", None)
    if default_review.get("state") == "confirmed":
        diagnostics.append(
            Diagnostic(
                "error",
                "review.confirmed-default",
                "confirmed review state cannot be inherited; confirm each Claim with a content digest",
                1,
                document.id,
            )
        )

    if "provenance" not in defaults:
        default_provenance: dict[str, Any] = {}
    elif not isinstance(defaults["provenance"], dict):
        diagnostics.append(Diagnostic("error", "provenance.type", "defaults.provenance must be a mapping"))
        default_provenance = {}
    else:
        default_provenance = defaults["provenance"]
    default_based_on = (
        _string_list(
            default_provenance["basedOn"],
            field_name="defaults.provenance.basedOn",
            address=document.id,
            diagnostics=diagnostics,
            line=1,
        )
        if "basedOn" in default_provenance
        else []
    )
    for reference in default_based_on:
        _validate_reference(
            reference,
            field_name="defaults.provenance.basedOn",
            address=document.id,
            diagnostics=diagnostics,
            line=1,
        )

    local_ids: set[str] = set()
    for claim in document.claims:
        address = f"{document.id}#{claim.id}"
        if claim.id in local_ids:
            diagnostics.append(Diagnostic("error", "id.duplicate", f"duplicate local ID {claim.id}", claim.line, address))
        local_ids.add(claim.id)
        override_review = (
            _review_mapping(
                claim.metadata["review"],
                address=address,
                diagnostics=diagnostics,
                line=claim.line,
            )
            if "review" in claim.metadata
            else {}
        )
        claim.effective_review = dict(default_review)
        claim.effective_review.update(override_review)
        claim.effective_based_on = _effective_based_on(
            default_based_on,
            claim.metadata,
            address=address,
            diagnostics=diagnostics,
            line=claim.line,
        )
        for reference in claim.effective_based_on:
            _validate_reference(
                reference,
                field_name="provenance.basedOn",
                address=address,
                diagnostics=diagnostics,
                line=claim.line,
            )
        own_review = claim.metadata.get("review")
        own_digest = own_review.get("contentDigest") if isinstance(own_review, dict) else None
        if own_digest is not None and claim.effective_review.get("state") != "confirmed":
            diagnostics.append(
                Diagnostic(
                    "error",
                    "review.digest-unexpected",
                    "review.contentDigest is only valid for a confirmed Claim",
                    claim.line,
                    address,
                )
            )
        if claim.effective_review.get("state") == "confirmed":
            expected = own_digest
            if not isinstance(expected, str):
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "review.digest-missing",
                        "confirmed Claim must include review.contentDigest",
                        claim.line,
                        address,
                    )
                )
            elif not re.fullmatch(r"sha256:[0-9a-f]{64}", expected):
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "review.digest-format",
                        "review.contentDigest must be sha256 followed by 64 lowercase hexadecimal characters",
                        claim.line,
                        address,
                    )
                )
            elif expected != claim.content_digest:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "review.stale",
                        "Claim content changed after confirmation",
                        claim.line,
                        address,
                    )
                )

    for relationship in document.relationships:
        address = f"{document.id}#{relationship.id}"
        if relationship.id in local_ids:
            diagnostics.append(
                Diagnostic("error", "id.duplicate", f"duplicate local ID {relationship.id}", relationship.line, address)
            )
        local_ids.add(relationship.id)
        relationship.effective_review = dict(default_review)
        if "review" in relationship.metadata:
            relationship.effective_review.update(
                _review_mapping(
                    relationship.metadata["review"],
                    address=address,
                    diagnostics=diagnostics,
                    line=relationship.line,
                )
            )
        relationship.effective_based_on = _effective_based_on(
            default_based_on,
            relationship.metadata,
            address=address,
            diagnostics=diagnostics,
            line=relationship.line,
        )
        for reference in relationship.effective_based_on:
            _validate_reference(
                reference,
                field_name="provenance.basedOn",
                address=address,
                diagnostics=diagnostics,
                line=relationship.line,
            )
        if not isinstance(relationship.metadata.get("type"), str):
            diagnostics.append(
                Diagnostic("error", "relationship.type", "relationship type must be a string", relationship.line, address)
            )
        target = relationship.metadata.get("target")
        if not isinstance(target, str):
            diagnostics.append(
                Diagnostic("error", "relationship.target", "relationship target must be a string", relationship.line, address)
            )
        else:
            _validate_reference(
                target,
                field_name="relationship target",
                address=address,
                diagnostics=diagnostics,
                line=relationship.line,
            )


def parse_text(text: str, *, source: str = "<string>") -> Document:
    if text.startswith("\ufeff"):
        raise DPlusError("UTF-8 BOM is not allowed", source=source, line=1)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise DPlusError("document must start with YAML frontmatter delimiter ---", source=source, line=1)
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise DPlusError("unterminated YAML frontmatter", source=source, line=1) from exc

    metadata = _yaml_mapping("\n".join(lines[1:closing]), source=source, line=2)
    required = {"formatVersion", "id", "type"}
    missing = sorted(required - set(metadata))
    if missing:
        raise DPlusError(f"missing required frontmatter keys: {', '.join(missing)}", source=source, line=2)
    if metadata.get("formatVersion") != "0.1":
        raise DPlusError(
            f"unsupported formatVersion {metadata.get('formatVersion')!r}",
            source=source,
            line=2,
        )
    if not isinstance(metadata.get("id"), str) or not ENTITY_ID_RE.fullmatch(metadata["id"]):
        raise DPlusError(f"invalid entity ID {metadata.get('id')!r}", source=source, line=2)
    if not isinstance(metadata.get("type"), str) or not metadata["type"]:
        raise DPlusError("type must be a non-empty string", source=source, line=2)
    if "title" in metadata:
        raise DPlusError("title belongs in the single H1, not frontmatter", source=source, line=2)

    body = lines[closing + 1 :]
    body_line_offset = closing + 2
    headings = _scan_headings(body, source=source, line_offset=body_line_offset)
    h1s = [item for item in headings if item.level == 1]
    if len(h1s) != 1:
        raise DPlusError("document must contain exactly one H1 title", source=source, line=body_line_offset)
    title_heading = h1s[0]
    if not title_heading.text:
        raise DPlusError("H1 title must not be empty", source=source, line=body_line_offset + title_heading.line_index)
    if any(item.line_index < title_heading.line_index for item in headings):
        raise DPlusError("H1 title must be the first heading", source=source, line=body_line_offset + title_heading.line_index)
    if any(line.strip() for line in body[: title_heading.line_index]):
        raise DPlusError("only blank lines may precede the H1 title", source=source, line=body_line_offset)

    h2s = [item for item in headings if item.level == 2]
    first_h2 = h2s[0].line_index if h2s else len(body)
    if any(line.strip() for line in body[title_heading.line_index + 1 : first_h2]):
        raise DPlusError(
            "content after the title must be inside Context, Claims, or Relationships",
            source=source,
            line=body_line_offset + title_heading.line_index + 1,
        )

    seen_sections: set[str] = set()
    last_order = -1
    for heading in h2s:
        if heading.text not in SECTION_ORDER:
            raise DPlusError(
                f"unsupported level-two section {heading.text!r}",
                source=source,
                line=body_line_offset + heading.line_index,
            )
        if heading.text in seen_sections:
            raise DPlusError(
                f"duplicate section {heading.text}",
                source=source,
                line=body_line_offset + heading.line_index,
            )
        order = SECTION_ORDER[heading.text]
        if order < last_order:
            raise DPlusError(
                "sections must appear in Context, Claims, Relationships order",
                source=source,
                line=body_line_offset + heading.line_index,
            )
        seen_sections.add(heading.text)
        last_order = order

    claims: list[Claim] = []
    relationships: list[Relationship] = []
    context: str | None = None
    for index, section in enumerate(h2s):
        end = h2s[index + 1].line_index if index + 1 < len(h2s) else len(body)
        if section.text == "Context":
            context_lines = body[section.line_index + 1 : end]
            _reject_reserved_fences(
                context_lines,
                source=source,
                line_offset=body_line_offset + section.line_index + 1,
                location="Context",
            )
            context_text = normalize_claim_markdown(context_lines)
            context = context_text or None
        elif section.text == "Claims":
            claims = list(
                _section_entries(
                    body,
                    headings,
                    section_start=section.line_index,
                    section_end=end,
                    source=source,
                    line_offset=body_line_offset,
                    kind="Claims",
                )
            )
        elif section.text == "Relationships":
            relationships = list(
                _section_entries(
                    body,
                    headings,
                    section_start=section.line_index,
                    section_end=end,
                    source=source,
                    line_offset=body_line_offset,
                    kind="Relationships",
                )
            )

    document = Document(
        source=source,
        metadata=metadata,
        title=title_heading.text,
        context=context,
        claims=claims,
        relationships=relationships,
    )
    _validate(document)
    return document


def parse_file(path: str | Path) -> Document:
    file_path = Path(path)
    return parse_text(file_path.read_text(encoding="utf-8"), source=str(file_path))
