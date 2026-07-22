#!/usr/bin/env python3
"""Bounded controller-private behavioral receipts for repository evaluations."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "shipworthy-runtime-receipt-v1"
MAX_EVENTS = 512
MAX_TEXT = 512
MAX_BYTES = 262_144
EVENT_TYPES = frozenset({
    "route_visit",
    "activation",
    "input",
    "surface_spawn",
    "transition",
    "reload_reentry",
    "blocked",
    "avoided",
})
FIELDS = frozenset({
    "event_type",
    "route",
    "role",
    "state",
    "viewport_class",
    "control",
    "input_mechanism",
    "surface",
    "behavior",
    "before_state",
    "after_state",
    "outcome",
    "reason",
})
CONTROL_FIELDS = frozenset({"identity", "type"})


class ReceiptError(ValueError):
    """Raised when a receipt event violates the closed private contract."""


def _validate_text(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ReceiptError(f"{field} must be a string")
    value = value.strip()
    if not value:
        raise ReceiptError(f"{field} must not be empty")
    if len(value) > MAX_TEXT:
        raise ReceiptError(f"{field} is too long")
    return value


def validate_event(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReceiptError("event must be an object")
    unknown = set(value) - FIELDS
    if unknown:
        raise ReceiptError(f"unknown field: {sorted(unknown)[0]}")
    event_type = _validate_text(value.get("event_type"), "event_type")
    if event_type not in EVENT_TYPES:
        raise ReceiptError("unsupported event_type")
    event: dict[str, Any] = {"event_type": event_type}
    for field in sorted(FIELDS - {"event_type", "control"}):
        if field in value:
            event[field] = _validate_text(value[field], field)
    if "control" in value:
        control = value["control"]
        if not isinstance(control, dict):
            raise ReceiptError("control must be an object")
        unknown_control = set(control) - CONTROL_FIELDS
        if unknown_control:
            raise ReceiptError(f"unknown control field: {sorted(unknown_control)[0]}")
        if set(control) != CONTROL_FIELDS:
            raise ReceiptError("control requires identity and type")
        event["control"] = {
            "identity": _validate_text(control["identity"], "control.identity"),
            "type": _validate_text(control["type"], "control.type"),
        }
    return event


def receipt_digest(receipt: dict[str, Any]) -> str:
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_events(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    """Return validated events from every reset epoch in execution order."""
    if not isinstance(receipt, dict) or receipt.get("schema_version") != SCHEMA_VERSION:
        raise ReceiptError("invalid receipt schema version")
    epochs = receipt.get("epochs")
    if not isinstance(epochs, list) or not epochs:
        raise ReceiptError("receipt requires at least one epoch")
    events: list[dict[str, Any]] = []
    for expected_id, epoch in enumerate(epochs, 1):
        if not isinstance(epoch, dict) or set(epoch) != {"id", "events"} or epoch.get("id") != expected_id:
            raise ReceiptError("receipt epoch sequence is invalid")
        epoch_events = epoch.get("events")
        if not isinstance(epoch_events, list) or len(epoch_events) > MAX_EVENTS:
            raise ReceiptError("receipt event limit exceeded")
        events.extend(validate_event(event) for event in epoch_events)
    return events


class RuntimeReceipt:
    """Atomic JSON receipt with deterministic epochs and no wall-clock fields."""

    def __init__(self, path: Path | str):
        self.path = Path(path).resolve()
        self._lock = threading.Lock()
        if not self.path.exists():
            self._write({"schema_version": SCHEMA_VERSION, "epochs": [{"id": 1, "events": []}]})
        else:
            self.read()

    def _write(self, value: dict[str, Any]) -> None:
        encoded = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        if len(encoded) > MAX_BYTES:
            raise ReceiptError("receipt byte limit exceeded")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        with temporary.open("wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, self.path)

    def read(self) -> dict[str, Any]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ReceiptError(f"invalid receipt: {error}") from error
        if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
            raise ReceiptError("invalid receipt schema version")
        epochs = value.get("epochs")
        if not isinstance(epochs, list) or not epochs:
            raise ReceiptError("receipt requires at least one epoch")
        for expected_id, epoch in enumerate(epochs, 1):
            if not isinstance(epoch, dict) or set(epoch) != {"id", "events"} or epoch.get("id") != expected_id:
                raise ReceiptError("receipt epoch sequence is invalid")
            events = epoch.get("events")
            if not isinstance(events, list) or len(events) > MAX_EVENTS:
                raise ReceiptError("receipt event limit exceeded")
            epoch["events"] = [validate_event(event) for event in events]
        return value

    def current_events(self) -> list[dict[str, Any]]:
        return self.read()["epochs"][-1]["events"]

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        clean = validate_event(event)
        with self._lock:
            receipt = self.read()
            events = receipt["epochs"][-1]["events"]
            if len(events) >= MAX_EVENTS:
                raise ReceiptError("receipt event limit exceeded")
            events.append(clean)
            self._write(receipt)
        return clean

    def reset(self) -> int:
        with self._lock:
            receipt = self.read()
            identifier = len(receipt["epochs"]) + 1
            receipt["epochs"].append({"id": identifier, "events": []})
            self._write(receipt)
        return identifier
