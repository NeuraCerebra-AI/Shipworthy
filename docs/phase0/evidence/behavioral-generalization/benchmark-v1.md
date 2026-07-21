# Behavioral benchmark v1 freeze

Frozen source revision: `4651c8d1cd006230788d0d37f0e3fc312e5fbe48`

Machine authority: `tests/skill_product/gauntlet/benchmark-v1.json`

This freeze preserves the original Gauntlet fixture, private oracles, and predecessor evidence byte-for-byte. It does not reinterpret the predecessor results:

- Runtime-only: `FAIL`; behavioral acceptance was not achieved.
- Full-evidence: `FAIL`; behavioral acceptance was not achieved.
- Specification review: `ISSUES`.
- Quality review: `ISSUES`.
- Filesystem containment: `NOT_PROVEN`.
- Oracle blindness: procedural only.

The benchmark now reports four independent diagnostic dimensions:

1. Discovery: whether material behavior was found.
2. Execution: whether safe behavior was actually exercised.
3. Defect detection: whether seeded defects were reported with supported lineage.
4. Evidence integrity: whether canonical artifacts, receipts, proof links, and closure are valid.

The official acceptance decision is categorical. No combined percentage can override a failed dimension, a false exhaustive closure, invalid artifacts, or a missed release-blocking defect.

The starting branch's stale regression expectations are preserved in the machine freeze while the executable test suite is calibrated to the actual starting revision. That calibration does not convert either historical native result to PASS.
