# Schema Relocation Ledger

The three versioned schemas were copied byte-for-byte into the orchestrator
reference closure. Root originals remain in place during this task.

| Schema | Source/destination SHA-256 | Semantic diff | Version decision |
| --- | --- | --- | --- |
| `browser-evidence-envelope.schema.json` | `bad61277f885bb7ba1437ab85e07edbc5a4454448e82aa664dde7005344c8024` | none | remain v1 (`1.0`) |
| `readiness-ledger.schema.json` | `73b92405402623ae7fc4ace475467df6cbb1b8f12b142ee7411405a4c8325115` | none | remain v1 (`1.0`) |
| `report-input.schema.json` | `82ba535fa07161b943f66b5f25a3ab8eccfb4ed78fe9b6412e074356aea5d0e1` | none | remain v1 (`1.0`) |

Semantic diff: none. Recursive field-by-field comparison found no added,
removed, reordered, or changed JSON values, so a schema-version increment is not
warranted.

## Golden Fixture Results

- Directly schema-valid: 2 v1 ledgers, 1 v1 report input, and 3 browser evidence
  envelopes (6 total).
- Rejected by the ledger schema: 5 hostile or inconsistent v1 fixtures (hostile
  path, inconsistent blocker, lying green, mismatched gate, and unknown enum).
- Structurally valid but conservatively classified by the documented semantic
  pass: 1 missing-artifact ledger. Its absent bytes remain evidence debt; the
  structural schema was not weakened or extended to hide it.
- Classified pre-transform rather than weakened into a schema: 1
  `legacy/readiness-v0` fixture and 2 `playwright/json-reporter` fixtures (3
  total). Their deterministic mappings produce post-transform inputs that must
  validate against the unchanged v1 schemas.

Golden validation uses the repository-only `tests/skill_product/support/schema_subset.py`
oracle and does not add an installed validator or importer.
