from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


CATEGORIES = ("finding_identity", "action", "proof", "gate", "counts", "html", "sarif", "bundle", "artifact_lineage")
EXPLAINED = {
    "sarif": "v1 adds stable record identity and gate metadata while preserving result meaning",
    "bundle": "canonical source bytes differ by format",
    "artifact_lineage": "v1 records explicit import lineage",
}


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("shipworthy_test_" + path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_id(row: dict[str, object]) -> str:
    title = str(row.get("title", "")).strip().lower()
    location = row.get("location") if isinstance(row.get("location"), dict) else {}
    discriminator = "|".join(
        str(value).strip().lower()
        for value in (location.get("file"), location.get("line"), row.get("section"))
        if value not in (None, "")
    )
    identity = title if not discriminator else f"{title}|{discriminator}"
    return "FND-LEGACY-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12].upper()


def project_legacy_to_v1_report(document: dict[str, object], source_digest: str) -> dict[str, object]:
    projected = json.loads(json.dumps(document))
    projected["schema_name"] = "shipworthy/readiness-report-projection"
    projected["schema_version"] = "1.0"
    projected["producer"] = {"name": "shipworthy-skill", "version": "1.0"}
    projected["artifact_lineage"] = {
        "operation": "legacy/readiness-v0-to-v1",
        "source_sha256": source_digest,
    }
    for row in projected.get("findings", []):
        if isinstance(row, dict):
            row["record_id"] = canonical_id(row)
            row["record_kind"] = "finding"
    return projected


def snapshot(document: dict[str, object], scripts: Path) -> dict[str, object]:
    renderer = _load(scripts / "render_report.py")
    sarif_module = _load(scripts / "to_sarif.py")
    bundle_module = _load(scripts / "make_bundle.py")
    raw = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    html = renderer.render(document).encode("utf-8")
    sarif = sarif_module.to_sarif(document)
    sarif_bytes = json.dumps(sarif, sort_keys=True, separators=(",", ":")).encode("utf-8")
    bundle = bundle_module.build_bundle_bytes(
        document,
        {"ledger.json": raw, "readiness-report.html": html, "readiness.sarif": sarif_bytes},
        str(document.get("generated_at", "1980-01-01T00:00:00Z")),
    )
    findings = [row for row in document.get("findings", []) if isinstance(row, dict)]
    failures, policy, confirmed = sarif_module.gate_failures(document)
    identities = tuple(str(row.get("record_id") or canonical_id(row)) for row in findings)
    return {
        "finding_identity": identities,
        "action": tuple(str(row.get("action", "Prove")) for row in findings),
        "proof": tuple(str(row.get("proof", "Not tested")) for row in findings),
        "gate": ("fail" if failures else "pass", tuple(sorted(policy)), confirmed),
        "counts": (len(findings), tuple(sorted((document.get("summary") or {}).items()))),
        "html": hashlib.sha256(html).hexdigest(),
        "sarif": hashlib.sha256(sarif_bytes).hexdigest(),
        "bundle": hashlib.sha256(bundle).hexdigest(),
        "artifact_lineage": document.get("artifact_lineage"),
    }


def compare(legacy: dict[str, object], v1: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    differences = []
    debt = []
    for category in CATEGORIES:
        if legacy[category] == v1[category]:
            continue
        explanation = EXPLAINED.get(category)
        row = {"category": category, "explained": explanation is not None, "explanation": explanation}
        differences.append(row)
        if explanation is None:
            payload = json.dumps([category, legacy[category], v1[category]], sort_keys=True, default=str).encode()
            debt.append({
                "difference_id": "DDR-" + hashlib.sha256(payload).hexdigest()[:12].upper(),
                "category": category,
                "reason": "Unexplained dual-render difference requires review.",
            })
    return differences, debt
