# Exhaustive Surface Gauntlet — frozen-revision acceptance

Date: 2026-07-19

Frozen revision: `63b01f87633beaba6e85ab712177f5e8ad83cb1b`

Result: **FAIL — no behavioral acceptance claim**

The one permitted post-`dd6a284` repair cycle changed only the current-run artifact gate. A RED contract test proved that the prior instructions did not explicitly forbid a list-shaped frontier or finding-only semantic aliases. The repair now requires an object-shaped canonical frontier and exact `shipworthy-semantic-v1` finding lineage. No later skill or harness repair was made.

## `dd6a284` failure classification

- **A — material path/control miss:** none. The subject observed every oracle-backed behavior.
- **B — finding-lineage/proof failure:** the subject wrote a legacy list-shaped `path_frontier`, so canonical row kinds, counts, closure, and exact finding lineage were absent even though narrative observations existed. This was the sole repair target.
- **C — oracle/comparator normalization problem:** none needed to explain the invalid `dd6a284` artifact; the comparator correctly rejected it.
- **D — valid extra discovery:** the runtime subject found the missing contextual import-cancellation path even though the oracle requires it only in full-evidence mode.

## Frozen confirmation results

| Mode | Native subject | Canonical artifact proof | Comparator result | Classification |
|---|---|---|---|---|
| runtime-only | `runtime_confirm_63b01f8` | 191 rows; 9 intents, 10 features, 37 surfaces, 87 controls, 48 transitions; identical top-level frontier in both JSON artifacts; `closed_multi_source`; exact finding lineage | `FAIL` | One A miss: admin/mobile Invite was sampled with zero attempts instead of directly exercised. C: context-menu control type and create/reload state-key variants were semantically equivalent but not normalized; four seeded findings used equivalent effect/key variants not accepted by the oracle. D: provider-managed profile editing and stale-session false success were valid extra discoveries. |
| full-evidence | `full_confirm_63b01f8` | 237 rows; 8 intents, 9 features, 52 surfaces, 81 controls, 87 transitions; identical top-level frontier in both JSON artifacts; `closed_multi_source`; all six seeded defects found plus two extras | `FAIL` | C: `comparison_view` reads a current canonical frontier only through `source_ledger.path_frontier`; this report used the contract-required top-level `path_frontier`, producing zero comparator rows. A read-only projection of that same frontier reduced the apparent misses to semantic-key aliases for paths directly exercised. D: stale Create success and stale Invite success were valid extra discoveries. No full-evidence A or B miss was established. |

The product verdict `NOT READY` is expected and correct for the deliberately defective fixture. Acceptance evaluates discovery, evidence, and closure—not whether the fixture itself is ready.

## Exact retained hashes

The harness forbids PASS evidence export when acceptance is `FAIL`, so raw artifacts remain temporary and are not represented as durable PASS evidence. These hashes identify the evaluated files before cleanup.

### Runtime-only

- `acceptance-result.json`: `d7858da18e4ac1bba5751b24502f1228add52994ea4632d267968b65496a678a`
- `comparison-packet.json`: `f636f79666fcebfef05bf663fe213df5b46f05a2a09880ca0b7f0c10caca58ec`
- `readiness-ledger.json`: `629dd326b3a3f695da1669a1ed33618971b5993531c7bf218919a3606cf53e1c`
- `report-input.json`: `6aa8b8ec9c995c2340c2436ba120b89fa48c4699f3f858d673027d590b5ef0b8`
- `report.html`: `f6b5ac3b2562e47b4a07c4d66ce6fccec97f168e5419ec22398dbb9d015f29ce`
- `run.log`: `a42fead38e30dfe4da6078089ae240e1e5549aa391b9c8dd6bd84333f037f991`

### Full-evidence

- `acceptance-result.json`: `2701c66e07d43316f0e7800dd0dbc81acee5a74e7891adc1bc426ff7372061e1`
- `comparison-packet.json`: `a13c0b794a7752265fd87f95127e9eda9c44781f5e9a81d10333270c18aafd11`
- `readiness-ledger.json`: `e00385fac97fafcc574252fb8c4d659b626d81317b3b2e4ed505b459d5d75ad6`
- `report-input.json`: `25d4410b9af111fa4f4bc7172d7be5792024970f57e9f9f4ba7a464fb63ef224`
- `report.html`: `66711f4822dfc50a0a14d03a9afbd76effec7321f038ff0148eade702422a6f3`
- `run.log`: `2cab63590960c88f66dcad9260d5ee0bf691e7f63cbfca456f080a93ca7dd527`

## Proof boundaries

- Native-agent dispatch and actual browser path-walking: proven for both confirmation modes.
- Canonical object shape and exact finding-row lineage: proven in both final artifacts.
- Runtime-only acceptance: **not passed** because of the A miss above.
- Full-evidence acceptance: **not passed** because the frozen comparator rejected the top-level canonical wrapper and remaining semantic aliases.
- Filesystem containment: `NOT_PROVEN`.
- Oracle blindness: procedural only, not technically enforced.
- Installed validator: not justified and not added.
- Durable six-artifact PASS export: not created because neither mode passed.
