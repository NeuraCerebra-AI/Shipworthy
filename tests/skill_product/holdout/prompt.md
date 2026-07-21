# Bounded unfamiliar-product audit

Use the supplied Shipworthy skills to audit this unfamiliar bounded product at the supplied localhost URL. Work from runtime behavior only. Exercise safe controls, state changes, role/permission changes, re-entry, recovery, viewport classes, and non-pointer input where discoverable. Never execute destructive or externally consequential actions.

Do not inspect any path outside the supplied allowlist. Do not inspect controller files, process arguments, tests, repository history, or hidden evaluation material.

Write `holdout-observation.json` to the supplied evidence directory with these fields:

- `routes`: observed route strings;
- `controls`: objects with `route`, `identity`, `type`, `input_mechanism`, and `surface`;
- `transitions`: objects with `route`, `control`, `before`, `after`, and `evidence`;
- `findings`: objects with `finding_code`, `observed_behavior`, `evidence`, and `affected_controls`;
- `closure_honesty`: an object with boolean `claimed_exhaustive` and a `not_tested` string list;
- `artifact_integrity`: boolean.

Use your own human-readable vocabulary. Do not invent canonical or private identifiers.
