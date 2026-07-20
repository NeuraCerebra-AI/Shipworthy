# Exhaustive Surface Gauntlet — unchanged-skill baseline

Date: 2026-07-19

Revision: `ad60c9f`

Native subject: `gauntlet_baseline_subject_d` (`fork_turns: none`)

Mode: `runtime-only`

Production skill changes before run: none

## Authoritative result

`FAIL` (finalize exit `1`). The subject completed with all three required
artifacts, the localhost target remained healthy, reset was verified, and the
private comparator independently derived `incomplete`.

The subject claimed `bounded_complete_with_blockers`; its JSON carried 5
features, 7 surfaces, 16 controls, and 13 transitions. The comparator reported:

- 17 of 17 runtime-required semantic identities missing;
- 41 unclassified rows;
- 7 unclassified findings;
- 4 expected defects unmatched by canonical lineage;
- JSON/HTML closure contradiction because the HTML lacked the required machine
  closure marker;
- procedural oracle blindness and filesystem containment `NOT_PROVEN`.

## Diagnostic causes

| Cause | Evidence | Required general repair |
|---|---|---|
| Frontier structure and identity | Every row used ad hoc dotted keys such as `control.save_real`; none used the versioned type-specific semantic keys. | One canonical versioned intent → feature → surface → control → transition frontier with deterministic keys and parent lineage. |
| Terminal vocabulary | Rows used `failed`, `missing`, `sampled_with_justification`, and other mixed outcome/finding terms. | Separate terminal coverage dispositions from readiness findings and validate allowed values. |
| Closure derivation | `bounded_complete_with_blockers` is outside the objective closure vocabulary and was self-declared despite structural drift. | Derive closure from row terminality, reconciliation, independent methods, and qualifying zero-yield passes. |
| Artifact reconciliation | Prose showed matching closure text, but HTML did not carry the machine-readable closure marker required by finalize. | Enforce exact JSON/HTML closure and count reconciliation. |
| Material-state census | The agent inventoried many controls but did not produce the required mobile/role/state semantic identity. | Census every material role, state, fixture, and viewport variant without treating cosmetic variants as new methods. |
| Safe-control exercise | Safe Publish and Export were marked `avoided`; prerequisite enablement and eventual publish were not proven. | Exercise every safe control once per materially different behavior; reserve `avoided` for unsafe/destructive actions. |
| Finding discipline | Expected successes, blocked feature flags, and normal avoided actions were emitted as findings alongside real defects. | Findings require material adverse effects; normal coverage dispositions remain frontier evidence, not findings. |
| Defect proof | Save loss and false affordance were found, but affected lineage did not match canonical product identities. | Require `affected_semantic_keys[]`, normalized effect code, and evidence references on material findings. |
| Report visibility | The HTML was readable and action-first, but coverage proof was bespoke and not contract-derived. | Add a compact human Product Coverage section derived from canonical rows, with bounded expandable detail. |

## Instrument history and non-aggregation

Runs A–C were discarded and never aggregated: A exposed coordinator process-
group teardown; B/C exposed fixture/comparator ambiguities that were repaired
with regression tests. Run D is the only frozen-instrument baseline used to
justify production changes.

## Installed validator necessity gate

Not justified at this point. Structural drift is proven, but the unchanged
skills had not yet received the canonical schema/instruction contract. Apply
the smaller schema and instruction repair first. Promote no installed script
unless a fresh post-repair subject still cannot produce a trustworthy frontier.
