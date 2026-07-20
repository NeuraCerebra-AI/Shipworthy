"""Small fail-closed JSON Schema oracle for repository contract tests only."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


MAX_DEPTH = 64
MAX_NODES = 100_000
MAX_REF_STEPS = 256
SUPPORTED_KEYWORDS = frozenset(
    {
        "$defs",
        "$id",
        "$ref",
        "$schema",
        "additionalProperties",
        "allOf",
        "anyOf",
        "const",
        "contains",
        "enum",
        "format",
        "if",
        "items",
        "maxItems",
        "maxLength",
        "maximum",
        "minItems",
        "minLength",
        "minimum",
        "not",
        "pattern",
        "properties",
        "required",
        "then",
        "title",
        "type",
        "uniqueItems",
        "x-shipworthy-runtime-constraints",
    }
)


class SchemaValidationError(ValueError):
    """The candidate does not satisfy the schema subset."""


class UnsupportedKeywordError(SchemaValidationError):
    """The schema uses a keyword outside the closed supported subset."""


class SchemaReferenceError(SchemaValidationError):
    """A reference is not a safe pointer within the loaded schema document."""


class SchemaLimitError(SchemaValidationError):
    """The schema or candidate exceeds repository-oracle resource bounds."""


def _walk_nodes(value: Any, depth: int = 0) -> int:
    if depth > MAX_DEPTH:
        raise SchemaLimitError(f"input exceeds maximum depth {MAX_DEPTH}")
    if isinstance(value, dict):
        return 1 + sum(_walk_nodes(item, depth + 1) for item in value.values())
    if isinstance(value, list):
        return 1 + sum(_walk_nodes(item, depth + 1) for item in value)
    return 1


def _check_schema_keywords(schema: Any, path: str = "$") -> None:
    if not isinstance(schema, dict):
        raise UnsupportedKeywordError(f"schema at {path} must be an object")
    unknown = set(schema) - SUPPORTED_KEYWORDS
    if unknown:
        raise UnsupportedKeywordError(
            f"unsupported schema keyword at {path}: {sorted(unknown)[0]}"
        )
    for keyword in ("allOf", "anyOf"):
        for index, child in enumerate(schema.get(keyword, [])):
            _check_schema_keywords(child, f"{path}.{keyword}[{index}]")
    for keyword in ("contains", "if", "items", "not", "then"):
        if keyword in schema:
            _check_schema_keywords(schema[keyword], f"{path}.{keyword}")
    for keyword in ("$defs", "properties"):
        children = schema.get(keyword, {})
        if not isinstance(children, dict):
            raise UnsupportedKeywordError(f"{path}.{keyword} must be an object")
        for name, child in children.items():
            _check_schema_keywords(child, f"{path}.{keyword}.{name}")


def _resolve_pointer(root: dict[str, Any], pointer: str, reference: str) -> dict[str, Any]:
    if pointer == "":
        return root
    if not pointer.startswith("/"):
        raise SchemaReferenceError(f"invalid JSON Pointer $ref: {reference}")
    current: Any = root
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise SchemaReferenceError(f"unresolved local $ref: {reference}")
        current = current[part]
    if not isinstance(current, dict):
        raise SchemaReferenceError(f"$ref target is not a schema object: {reference}")
    return current


class _Resolver:
    """Resolve local pointers and same-directory schema files without network I/O."""

    def __init__(self, root_path: Path, root_schema: dict[str, Any]):
        self.directory = root_path.parent.resolve()
        self.cache = {root_path.resolve(): root_schema}

    def _load(self, path: Path) -> dict[str, Any]:
        if path not in self.cache:
            if not path.is_file():
                raise SchemaReferenceError(f"schema file does not exist: {path.name}")
            if path.stat().st_size > 1_000_000:
                raise SchemaLimitError("schema exceeds 1 MiB")
            try:
                schema = json.loads(path.read_bytes())
            except (OSError, json.JSONDecodeError) as error:
                raise SchemaReferenceError(f"cannot load referenced schema: {path.name}") from error
            if not isinstance(schema, dict):
                raise SchemaReferenceError(f"referenced schema is not an object: {path.name}")
            if _walk_nodes(schema) > MAX_NODES:
                raise SchemaLimitError(f"schema exceeds {MAX_NODES} nodes")
            _check_schema_keywords(schema)
            self.cache[path] = schema
        return self.cache[path]

    def resolve(
        self, current_path: Path, reference: str
    ) -> tuple[dict[str, Any], dict[str, Any], Path]:
        if not isinstance(reference, str) or not reference:
            raise SchemaReferenceError("$ref must be a non-empty string")
        if reference.startswith("#"):
            document = self._load(current_path)
            return _resolve_pointer(document, reference[1:], reference), document, current_path

        split = urlsplit(reference)
        if split.scheme or split.netloc or split.query:
            raise SchemaReferenceError("remote or parameterized $ref values are forbidden")
        relative = Path(split.path)
        if relative.is_absolute() or not split.path or ".." in relative.parts:
            raise SchemaReferenceError("$ref must name a same-directory schema file")
        target_path = (current_path.parent / relative).resolve()
        try:
            target_path.relative_to(self.directory)
        except ValueError as error:
            raise SchemaReferenceError("$ref escapes the schema directory") from error
        if target_path.parent != self.directory:
            raise SchemaReferenceError("$ref must remain in the same schema directory")
        document = self._load(target_path)
        return _resolve_pointer(document, split.fragment and f"/{split.fragment.removeprefix('/')}" or "", reference), document, target_path


def _matches_type(value: Any, expected: str) -> bool:
    types = {
        "array": lambda item: isinstance(item, list),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "null": lambda item: item is None,
        "number": lambda item: isinstance(item, (int, float))
        and not isinstance(item, bool),
        "object": lambda item: isinstance(item, dict),
        "string": lambda item: isinstance(item, str),
        "boolean": lambda item: isinstance(item, bool),
    }
    if expected not in types:
        raise UnsupportedKeywordError(f"unsupported type value: {expected}")
    return types[expected](value)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate(
    value: Any,
    schema: dict[str, Any],
    document: dict[str, Any],
    resolver: _Resolver,
    schema_path: Path,
    path: str,
    depth: int,
    ref_steps: int,
) -> None:
    if depth > MAX_DEPTH:
        raise SchemaLimitError(f"validation exceeds maximum depth {MAX_DEPTH}")
    if "$ref" in schema:
        if ref_steps >= MAX_REF_STEPS:
            raise SchemaLimitError(f"validation exceeds {MAX_REF_STEPS} reference steps")
        target, target_document, target_path = resolver.resolve(schema_path, schema["$ref"])
        _validate(
            value,
            target,
            target_document,
            resolver,
            target_path,
            path,
            depth + 1,
            ref_steps + 1,
        )

    if "type" in schema and not _matches_type(value, schema["type"]):
        raise SchemaValidationError(f"{path}: expected {schema['type']}")
    if "const" in schema and value != schema["const"]:
        raise SchemaValidationError(f"{path}: does not equal const")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaValidationError(f"{path}: value is not in enum")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise SchemaValidationError(f"{path}: string is too short")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise SchemaValidationError(f"{path}: string is too long")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise SchemaValidationError(f"{path}: string does not match pattern")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as error:
                raise SchemaValidationError(f"{path}: invalid date-time") from error
        elif "format" in schema:
            raise UnsupportedKeywordError(f"unsupported format: {schema['format']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise SchemaValidationError(f"{path}: number is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise SchemaValidationError(f"{path}: number is above maximum")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise SchemaValidationError(f"{path}: array has too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise SchemaValidationError(f"{path}: array has too many items")
        if schema.get("uniqueItems"):
            canonical = [_canonical(item) for item in value]
            if len(canonical) != len(set(canonical)):
                raise SchemaValidationError(f"{path}: array items are not unique")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate(item, schema["items"], document, resolver, schema_path, f"{path}[{index}]", depth + 1, ref_steps)
        if "contains" in schema:
            if not any(_is_valid(item, schema["contains"], document, resolver, schema_path, depth + 1, ref_steps) for item in value):
                raise SchemaValidationError(f"{path}: array does not contain a matching item")

    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [name for name in required if name not in value]
        if missing:
            raise SchemaValidationError(f"{path}: missing required property {missing[0]}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                raise SchemaValidationError(f"{path}: unexpected property {sorted(extras)[0]}")
        for name, child_schema in properties.items():
            if name in value:
                _validate(
                    value[name], child_schema, document, resolver, schema_path, f"{path}.{name}", depth + 1, ref_steps
                )

    for child in schema.get("allOf", []):
        _validate(value, child, document, resolver, schema_path, path, depth + 1, ref_steps)
    if "anyOf" in schema and not any(
        _is_valid(value, child, document, resolver, schema_path, depth + 1, ref_steps)
        for child in schema["anyOf"]
    ):
        raise SchemaValidationError(f"{path}: no anyOf branch matched")
    if "not" in schema and _is_valid(value, schema["not"], document, resolver, schema_path, depth + 1, ref_steps):
        raise SchemaValidationError(f"{path}: forbidden not branch matched")
    if "if" in schema and _is_valid(value, schema["if"], document, resolver, schema_path, depth + 1, ref_steps):
        if "then" in schema:
            _validate(value, schema["then"], document, resolver, schema_path, path, depth + 1, ref_steps)


def _is_valid(
    value: Any,
    schema: dict[str, Any],
    document: dict[str, Any],
    resolver: _Resolver,
    schema_path: Path,
    depth: int,
    ref_steps: int,
) -> bool:
    try:
        _validate(value, schema, document, resolver, schema_path, "$probe", depth, ref_steps)
    except (UnsupportedKeywordError, SchemaReferenceError, SchemaLimitError):
        raise
    except SchemaValidationError:
        return False
    return True


def validate(instance: Any, schema_path: Path) -> None:
    """Validate a JSON-like value against one bounded, local schema document."""

    schema_path = Path(schema_path)
    if not schema_path.is_file():
        raise SchemaReferenceError(f"schema file does not exist: {schema_path}")
    if schema_path.stat().st_size > 1_000_000:
        raise SchemaLimitError("schema exceeds 1 MiB")
    schema = json.loads(schema_path.read_bytes())
    if _walk_nodes(schema) > MAX_NODES:
        raise SchemaLimitError(f"schema exceeds {MAX_NODES} nodes")
    if _walk_nodes(instance) > MAX_NODES:
        raise SchemaLimitError(f"input exceeds {MAX_NODES} nodes")
    _check_schema_keywords(schema)
    resolver = _Resolver(schema_path.resolve(), schema)
    _validate(instance, schema, schema, resolver, schema_path.resolve(), "$", 0, 0)


def semantic_diff(left: Any, right: Any, path: str = "$") -> list[str]:
    """Return deterministic field-level differences between JSON-like values."""

    if type(left) is not type(right):
        return [f"{path}: {left!r} != {right!r}"]
    if isinstance(left, dict):
        differences: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}"
            if key not in left:
                differences.append(f"{child}: missing left")
            elif key not in right:
                differences.append(f"{child}: missing right")
            else:
                differences.extend(semantic_diff(left[key], right[key], child))
        return differences
    if isinstance(left, list):
        differences = []
        for index in range(max(len(left), len(right))):
            child = f"{path}[{index}]"
            if index >= len(left):
                differences.append(f"{child}: missing left")
            elif index >= len(right):
                differences.append(f"{child}: missing right")
            else:
                differences.extend(semantic_diff(left[index], right[index], child))
        return differences
    return [] if left == right else [f"{path}: {left!r} != {right!r}"]
