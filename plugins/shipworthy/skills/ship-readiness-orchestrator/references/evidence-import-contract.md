# Evidence Import Contract

Use this mapping only for browser, Playwright, or legacy structured input. Read
the complete supplied input once; cap it at 16 MiB, 100,000 aggregate values,
1,024 results, 1,024 attachments, and 64 levels of nesting. Reject malformed,
truncated, over-limit, ambiguous-version, or path-escaping input without partial
acceptance.

## Supported Input Mapping

- `shipworthy/browser-evidence-envelope` `1.0` is post-transform. Validate it
  directly with `schemas/browser-evidence-envelope.schema.json`; preserve host,
  target fingerprint, producer, steps, artifact descriptors, limitations,
  unavailable channels, finding IDs, and `not_proven` statements.
- `playwright/json-reporter` is pre-transform. Map project/suite/spec/test/result
  names and observed status into bounded steps; map supplied screenshots, traces,
  recordings, and other attachments only when their bytes are locally available.
  Record Playwright and the mapping procedure as distinct producer/lineage hops.
- `legacy/readiness-v0` is pre-transform. Map target, generated time, summary,
  verdict, coverage, and findings deterministically into a v1 ledger. Preserve
  unmapped or ambiguous values as evidence debt. The normalized v1 ledger is
  post-transform and must pass `schemas/readiness-ledger.schema.json` before use.

For every accepted artifact, record a safe relative path, media type, byte size,
SHA-256 digest, producer, operation, and source IDs. A URL, provider identifier,
report claim, or remote link is not local content and must never be marked as
locally available or locally integrity-checked. Missing bytes remain missing or
externally linked with explicit evidence debt.

Imported status is observation, not independent proof. Never inflate confidence,
severity, verifier approval, gate status, or readiness from a passing browser or
Playwright result. The proof ceiling is the narrowest target, fixture, role,
browser, action sequence, assertion, and artifact boundary actually evidenced.
Retain the original input digest and deterministic mapping notes so a reviewer
can reproduce each lineage hop.
