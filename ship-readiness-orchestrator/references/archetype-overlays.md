# Archetype overlays — seeding the path universe with priors (not checklists)

`profiles/*.json` are **archetype priors**: for a known kind of product (checkout, auth,
ai-chat, dashboard, …) they list the user intents, critical paths, common failure modes,
and *frequently-missing* paths that products of that type tend to have. They exist to make
path **discovery** sharper — so the audit surfaces the expected-goal-with-no-path findings
that are this tool's signature — without ever degrading into a fill-in-the-blanks checklist.

## How to use a profile

1. **Select by behavior, not by name.** Match a profile to what the target actually is and
   does. Partial matches are fine; multiple profiles can combine (an app with auth **and** a
   dashboard loads both). If nothing fits, run generic discovery with no profile.
2. **Add its items as hypotheses to the discovered path universe** (Mandatory Flow step 7),
   tagged with provenance `archetype:<name>` so the ledger shows which paths were
   product-discovered vs. profile-suggested. Each `expected_intent` and `often_missing_path`
   becomes a question to investigate: *does a path exist for this? if so, does it hold up?*
3. **Probe the `common_failure_modes`** on the relevant paths — they are things to *attempt*,
   not findings to assert.
4. **Resolve every hypothesis with real evidence**, exactly like any other path.

## Guardrails (these are what keep it honest — do not skip)

- **Profiles expand discovery; they never replace it.** Independent, product-specific path
  discovery still runs in full. A profile is a *floor* of things to check, never a ceiling —
  paths the product has that the profile doesn't list are audited all the same.
- **A profile item is never "covered" or "passed" without evidence.** The evidence rules are
  unchanged: an unverified profile hypothesis is `inferred`, `missing`, or `evidence_debt` —
  not `covered`. Suggesting a path and confirming a path are different acts.
- **A `common_failure_mode` is a probe, not a finding.** You still have to reproduce or
  observe the failure on *this* target before it enters the ledger. Never log a profile's
  generic failure as if you saw it here.
- **Profiles are not a scorecard.** "6 of 8 expected intents present" is not a readiness
  verdict and must never be rendered as one. The verdict comes from evidence, as always.
- **Absence can be legitimate.** If the product intentionally omits a profile intent (e.g., a
  checkout with deliberately no guest flow), that is a scope note, not an automatic
  missing-path blocker. Apply judgment; say what you assumed.
- **Don't let the profile blinker you.** If the profile pulls attention toward its listed
  areas and away from a product-specific risk, that's a failure of the overlay. The overlay
  serves discovery; it does not bound it.

## What ships

`checkout`, `auth`, `ai-chat`, `dashboard`. Each file carries `expected_intents`,
`critical_paths`, `common_failure_modes`, `often_missing_paths`, `high_risk_areas`, and
`evidence_cautions` (paths that are typically unsafe to exercise — real payments, real
emails, real account lockout — which map to `blocked`/`avoided` → evidence debt). The set is
meant to grow; a new profile is just another JSON file with those keys.
