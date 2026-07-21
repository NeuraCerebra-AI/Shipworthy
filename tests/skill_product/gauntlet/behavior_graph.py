#!/usr/bin/env python3
"""Structural behavior graph normalization and deterministic matching."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from typing import Iterable
from urllib.parse import unquote, urlsplit


ROLE_ALIASES = {"administrator": "admin", "workspace-owner": "admin", "standard-user": "member"}
VIEWPORT_ALIASES = {
    "phone": "mobile", "small": "mobile", "mobile": "mobile",
    "tablet": "tablet", "medium": "tablet",
    "desktop": "desktop", "large": "desktop", "wide": "desktop",
}
INPUT_ALIASES = {
    "mouse": "pointer", "mouse-click": "pointer", "click": "pointer", "pointer": "pointer", "tap": "pointer",
    "right-click": "secondary-pointer", "secondary-click": "secondary-pointer", "contextmenu": "secondary-pointer",
    "keyboard": "keyboard", "keyboard-shortcut": "keyboard", "shortcut": "keyboard", "meta-k-shortcut": "keyboard",
    "programmatic": "programmatic", "browser": "browser", "browser-reload": "browser",
}
CONTROL_TYPE_ALIASES = {
    "submit": "button", "menuitem": "button", "push-button": "button",
    "keyboard-shortcut": "keyboard", "browser-control": "browser",
}


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip().casefold()
    pieces: list[str] = []
    separated = False
    for character in text:
        if unicodedata.category(character)[0] in {"L", "N"}:
            if separated and pieces:
                pieces.append("-")
            pieces.append(character)
            separated = False
        else:
            separated = True
    return "".join(pieces).strip("-")


def _alias(value: object, aliases: dict[str, str]) -> str:
    normalized = normalize_text(value)
    for key, canonical in aliases.items():
        if normalized == key or normalized.startswith(key + "-"):
            return canonical
    return normalized


def normalize_route(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip()
    parsed = urlsplit(text if "://" in text else "https://local.invalid/" + text.lstrip("/"))
    segments: list[str] = []
    for raw in parsed.path.split("/"):
        if not raw:
            continue
        decoded = unicodedata.normalize("NFKC", unquote(raw)).casefold()
        decoded = decoded.replace("/", "%2f")
        segments.append(decoded)
    return "/" + "/".join(segments) if segments else "/"


def normalize_viewport(value: object) -> str:
    return _alias(value, VIEWPORT_ALIASES)


def normalize_input(value: object) -> str:
    return _alias(value, INPUT_ALIASES)


def normalize_role(value: object) -> str:
    return _alias(value, ROLE_ALIASES)


def normalize_control_type(value: object) -> str:
    return _alias(value, CONTROL_TYPE_ALIASES)


@dataclass(frozen=True)
class BehaviorNode:
    kind: str
    semantic_key: str = ""
    route: str = ""
    role: str = ""
    state: str = ""
    viewport: str = ""
    control_identity: str = ""
    control_type: str = ""
    input_mechanism: str = ""
    surface: str = ""
    behavior: str = ""
    before_state: str = ""
    after_state: str = ""
    evidence_links: tuple[str, ...] = ()


@dataclass(frozen=True)
class Match:
    status: str
    index: int | None = None
    candidate_indexes: tuple[int, ...] = ()


def _normalized(node: BehaviorNode) -> BehaviorNode:
    return BehaviorNode(
        kind=normalize_text(node.kind),
        semantic_key=node.semantic_key,
        route=normalize_route(node.route) if node.route else "",
        role=normalize_role(node.role),
        state=normalize_text(node.state),
        viewport=normalize_viewport(node.viewport),
        control_identity=normalize_text(node.control_identity),
        control_type=normalize_control_type(node.control_type),
        input_mechanism=normalize_input(node.input_mechanism),
        surface=normalize_text(node.surface),
        behavior=normalize_text(node.behavior),
        before_state=normalize_text(node.before_state),
        after_state=normalize_text(node.after_state),
        evidence_links=node.evidence_links,
    )


def _accepted(value: str, expected: str, aliases: Iterable[str], normalizer=normalize_text) -> bool:
    if not expected:
        return True
    accepted = {normalizer(expected), *(normalizer(alias) for alias in aliases)}
    return normalizer(value) in accepted


def _structural_match(expected: BehaviorNode, actual: BehaviorNode, aliases: Iterable[str], behavior_aliases: Iterable[str]) -> bool:
    left, right = _normalized(expected), _normalized(actual)
    if left.kind != right.kind:
        return False
    for field in ("route", "role", "state", "viewport", "surface", "before_state", "after_state"):
        wanted = getattr(left, field)
        observed = getattr(right, field)
        if wanted and observed and wanted != observed:
            return False
        if wanted and not observed:
            return False
    if left.control_identity and not _accepted(right.control_identity, left.control_identity, aliases):
        return False
    if left.control_type and left.control_type != right.control_type:
        return False
    if left.input_mechanism and left.input_mechanism != right.input_mechanism:
        return False
    if left.behavior and not _accepted(right.behavior, left.behavior, behavior_aliases):
        return False
    return True


def match_behavior(
    expected: BehaviorNode,
    candidates: Iterable[BehaviorNode],
    *,
    aliases: Iterable[str] = (),
    behavior_aliases: Iterable[str] = (),
) -> Match:
    candidates = list(candidates)
    if expected.semantic_key:
        exact = [index for index, candidate in enumerate(candidates) if candidate.semantic_key == expected.semantic_key]
        if len(exact) == 1:
            return Match("exact", exact[0])
        if len(exact) > 1:
            return Match("ambiguous", candidate_indexes=tuple(exact))
        if candidates and all(candidate.semantic_key for candidate in candidates):
            return Match("key_mismatch")
    matched = [
        index for index, candidate in enumerate(candidates)
        if _structural_match(expected, candidate, aliases, behavior_aliases)
    ]
    if len(matched) == 1:
        return Match("equivalent", matched[0])
    if len(matched) > 1:
        return Match("ambiguous", candidate_indexes=tuple(matched))
    return Match("missing")


def parse_semantic_key(key: str, *, evidence_links: Iterable[str] = ()) -> BehaviorNode:
    parts = key.split(":")
    if parts[0] == "feature" and len(parts) >= 2:
        return BehaviorNode("feature", key, control_identity=parts[1], evidence_links=tuple(evidence_links))
    if parts[0] == "surface" and len(parts) >= 6:
        return BehaviorNode("surface", key, route=parts[1], state=parts[2], role=parts[3], viewport=parts[4], evidence_links=tuple(evidence_links))
    if parts[0] == "control" and len(parts) >= 9 and parts[1] == "surface":
        return BehaviorNode("control", key, route=parts[2], state=parts[3], role=parts[4], viewport=parts[5], control_identity=parts[6], control_type=parts[7], behavior=parts[8], evidence_links=tuple(evidence_links))
    if parts[0] == "transition" and len(parts) >= 12 and parts[2:4] == ["control", "surface"]:
        return BehaviorNode("transition", key, route=parts[4], state=parts[5], role=parts[6], viewport=parts[7], control_identity=parts[8], control_type=parts[9], behavior=parts[10], before_state=parts[1], after_state=parts[11], evidence_links=tuple(evidence_links))
    return BehaviorNode(parts[0] if parts else "unknown", key, evidence_links=tuple(evidence_links))


def node_from_receipt(event: dict) -> BehaviorNode:
    control = event.get("control") if isinstance(event.get("control"), dict) else {}
    event_type = event.get("event_type", "")
    kind = "transition" if event_type in {"transition", "reload_reentry"} else "control" if event_type in {"activation", "input", "blocked", "avoided"} else "surface"
    return BehaviorNode(
        kind=kind,
        route=event.get("route", ""),
        role=event.get("role", ""),
        state=event.get("state", ""),
        viewport=event.get("viewport_class", ""),
        control_identity=control.get("identity", ""),
        control_type=control.get("type", ""),
        input_mechanism=event.get("input_mechanism", ""),
        surface=event.get("surface", ""),
        behavior=event.get("behavior", ""),
        before_state=event.get("before_state", ""),
        after_state=event.get("after_state", ""),
    )


def verify_execution_claim(item: dict, row: dict, events: Iterable[dict]) -> Match:
    """Require private action support for one terminal report claim."""
    status = row.get("status", "")
    kind = item.get("kind", "")
    allowed_event_types: set[str]
    if status == "blocked":
        allowed_event_types = {"blocked"}
    elif status == "avoided":
        allowed_event_types = {"avoided"}
    elif kind == "surface":
        allowed_event_types = {"route_visit", "surface_spawn"}
    elif kind == "transition":
        allowed_event_types = {"transition", "reload_reentry"}
    elif kind == "control":
        allowed_event_types = {"activation", "input"}
    else:
        return Match("not_required")
    selected_events = [event for event in events if event.get("event_type") in allowed_event_types]
    candidates = [node_from_receipt(event) for event in selected_events]
    expected = parse_semantic_key(row.get("semantic_key") or item["semantic_key"])
    expected = replace(
        expected,
        semantic_key="",
        state="",
        surface="",
        before_state="" if kind == "transition" else expected.before_state,
        after_state="" if kind == "transition" else expected.after_state,
    )
    if item.get("identity"):
        expected = replace(expected, control_identity=item["identity"])
    if status in {"blocked", "avoided"}:
        expected = replace(expected, behavior="", input_mechanism="")
    if kind == "surface":
        expected = replace(expected, state="", control_identity="", control_type="", behavior="")
        spawned = normalize_text(item.get("disambiguator", "")) not in {"", "deep-route", "route"}
        if spawned:
            expected = replace(expected, surface=item.get("disambiguator", ""))
    if kind == "transition":
        expected = replace(expected, control_identity="", control_type="", input_mechanism="")
    match = match_behavior(
        expected,
        candidates,
        aliases=item.get("accepted_aliases", ()),
        behavior_aliases=item.get("receipt_behavior_aliases", ()),
    )
    return Match("supported", match.index, match.candidate_indexes) if match.status in {"exact", "equivalent"} else match


def _event_field(event: dict, field: str) -> object:
    if field == "event_types":
        return event.get("event_type", "")
    if field == "routes":
        return event.get("route", "")
    if field == "roles":
        return event.get("role", "")
    if field == "viewports":
        return event.get("viewport_class", "")
    if field == "control_identities":
        control = event.get("control") if isinstance(event.get("control"), dict) else {}
        return control.get("identity", "")
    if field == "control_types":
        control = event.get("control") if isinstance(event.get("control"), dict) else {}
        return control.get("type", "")
    if field == "input_mechanisms":
        return event.get("input_mechanism", "")
    return event.get(field.rstrip("s"), "")


def _clause_matches(event: dict, clause: dict) -> bool:
    normalizers = {
        "routes": normalize_route,
        "roles": normalize_role,
        "viewports": normalize_viewport,
        "control_types": normalize_control_type,
        "input_mechanisms": normalize_input,
    }
    allowed_fields = {
        "event_types", "routes", "roles", "viewports", "control_identities", "control_types",
        "input_mechanisms", "surfaces", "behaviors", "outcomes", "reasons", "states",
        "before_states", "after_states",
    }
    if set(clause) - allowed_fields:
        return False
    for field, accepted in clause.items():
        if not isinstance(accepted, list) or not accepted:
            return False
        normalizer = normalizers.get(field, normalize_text)
        observed = normalizer(_event_field(event, field))
        if observed not in {normalizer(value) for value in accepted}:
            return False
    return True


def verify_private_expectation(expectation: dict, events: Iterable[dict]) -> Match:
    """Match ordered private behavior clauses without exposing canonical IDs."""
    clauses = expectation.get("clauses") if isinstance(expectation, dict) else None
    if not isinstance(clauses, list) or not clauses:
        return Match("missing")
    events = list(events)
    matched: list[int] = []
    cursor = 0
    for clause in clauses:
        found = next((index for index in range(cursor, len(events)) if _clause_matches(events[index], clause)), None)
        if found is None:
            return Match("missing", candidate_indexes=tuple(matched))
        matched.append(found)
        cursor = found + 1
    return Match("supported", matched[-1], tuple(matched))
