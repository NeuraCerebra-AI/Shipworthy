# ship-deep-review

**The evidence engine.** A repo-agnostic, multi-wave review controller with one hard rule:

> No wave summary is written until every agent output has been read, a claim ledger exists, and an **independent verifier** has shadow-read the raw outputs against that ledger.

Claim ledger = truth layer. Coverage matrix = scope layer. Evidence-debt register = uncertainty layer. Prose is only the delivery layer, and it must trace back to those artifacts and pass a drift check before it's considered complete. Within Shipworthy it owns wave barriers, verifier gates, and final synthesis.

**Use it alone when** you want a hostile, multi-wave review, a release-readiness audit, an implementation-plan critique, or research validation of a substantive target. → See [`SKILL.md`](SKILL.md).
