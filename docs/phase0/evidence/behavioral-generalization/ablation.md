# Instruction ablation and HTML confidence evidence

## Frozen pre-ablation footprint

Measured across every installed file under the four repository skill trees,
excluding cache directories:

| Skill | Lines | Words | Bytes |
|---|---:|---:|---:|
| `ship-deep-review` | 578 | 4,746 | 32,755 |
| `ship-product-workflows` | 1,662 | 10,730 | 77,666 |
| `ship-readiness-orchestrator` | 5,195 | 31,475 | 286,020 |
| `ship-workflow-clarity` | 1,454 | 8,524 | 61,372 |
| **Total** | **8,889** | **55,475** | **457,813** |

## Candidate 1 — consolidate repeated behavioral closure wording

Temporary copy: `/private/tmp/shipworthy-ablation-candidate-1.FUEYQK`

Production file tested: `ship-product-workflows/SKILL.md`

The candidate replaced the repeated control-census, canonical-identity,
row-level reconciliation, and second closure-checklist blocks with one early
**Behavioral Proof Gate**. Detailed identity and frontier mechanics remain in
the already-required `references/path-discovery-and-coverage.md`.

Temporary-copy result:

- product skill: 19,770 → 16,244 bytes;
- product skill: 2,599 → 2,089 words;
- exhaustive-surface contract: 20/20 passed against the temporary skill root;
- generalized repair: inventory discoverable handlers, probe context-conventional input alternatives, and record negative attempts because omission does not prove absence;
- generalized lineage repair: one finding per independently fixable defect even when an action or artifact exposes several defects.

The first holdout baseline supplies the RED behavioral evidence for both repairs:
`Ctrl+Enter` was not discovered or executed, and the still-enabled submit after
permission loss was observed but merged into another finding. The final blind
holdout run is the single paired native behavioral comparison for this
candidate. No fixture label, route, or oracle identifier appears in the skill.

Decision: **keep**. No second or third candidate was run; further wording churn
was not justified by a demonstrated safety or reliability need.

## Post-change footprint before final reviews

After the retained ablation and the HTML confidence-summary implementation:

- total: 8,898 lines, 55,132 words, 457,253 bytes;
- byte change: **−560**;
- word change: **−343**;
- installed file count and the four public skill names are unchanged.

The line count rises slightly because the deterministic renderer uses readable
code and CSS, while the installed byte and word footprint both shrink. Recount
after review repairs before the final report; the final gate remains no larger
than 457,813 bytes unless an evidenced safety requirement is documented.

## Final installed footprint

The final review repairs touched repository-only evaluation code and evidence,
not the four production skill trees. The final footprint is therefore 8,908
lines, 55,187 words, and 457,759 bytes: 54 bytes and 288 words below the frozen
pre-ablation ceiling, with the same installed file set.

## HTML readability

Focused renderer tests verify canonical derivation, bounded content, escaping,
closure consistency, no default JavaScript, and action-first ordering. Direct
browser inspection covered:

- 1,440 × 1,000 desktop: concise confidence card, findings remain immediately below;
- 390 × 844 narrow viewport: labels stack without horizontal clipping;
- print media at 816 × 1,056: dark-on-light title, confidence labels, and white bounded cards after repairing a white-on-white title and ink-heavy confidence panel found during the first print inspection.

The large frontier remains in collapsed native details or bounded JSON. No
external resource or JavaScript was added.
