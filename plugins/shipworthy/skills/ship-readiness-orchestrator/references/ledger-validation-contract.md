# Ledger Validation Contract

Use the schema JSON as structural authority before structured render or import:

- `schemas/readiness-ledger.schema.json` for `shipworthy/readiness-ledger`.
- `schemas/report-input.schema.json` for `shipworthy/readiness-report-input`.
- `schemas/browser-evidence-envelope.schema.json` for a normalized browser envelope.

Read the complete input once, cap it at 16 MiB, 100,000 aggregate values, 1,024
artifacts, and 512 findings, and stop on excessive nesting, malformed JSON, an
unknown schema name/version, unsupported schema behavior, or a non-local schema
reference. Apply every declared constraint; do not add permissive defaults or
silently discard extra fields. Version `1.0` is the supported structured ledger
and report-input version.

Final shapes differ: `readiness-ledger.json` is the canonical ledger with
top-level `path_frontier`; `report-input.json` is the closed 1.0 wrapper whose
`source_ledger` is structurally identical. Do not add sibling frontier or
checkpoint fields to that wrapper.

After structural validation, check identity uniqueness and every cross-reference:
finding artifact IDs must resolve, lineage source IDs must name declared inputs,
and the gate, completion status, evidence debt, and readiness disposition must
agree. Preserve the declared producer and lineage through projection. Missing,
external, or unverifiable material stays evidence debt and cannot raise the
proof ceiling, confidence, verifier status, or readiness disposition.
Every evidence reference is a safe relative path to an existing non-empty file
under the evidence output, with only an optional fragment suffix. Each non-intent
frontier row names the correct immediate parent, and its semantic key is derived
mechanically from that parent under `shipworthy-semantic-v1`.

Render only the validated post-transform ledger/report input. On failure, retain
the source unchanged, report a bounded field path and reason, and request a
corrected or explicitly mapped input. Validation never authorizes execution,
remote retrieval, or mutation of the audited target.
