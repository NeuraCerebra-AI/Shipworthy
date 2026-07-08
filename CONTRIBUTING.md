# Contributing to Shipworthy

Thanks for helping make product-readiness auditing honest. A few disciplines keep this suite trustworthy — please read these before opening a PR.

## The prime directive: one truth layer

Shipworthy is one orchestrator + three lanes that feed **a single evidence ledger**. The fastest way to break it is to add a second source of truth. Before adding logic to a lane, read [`docs/architecture.md`](docs/architecture.md). Lanes return evidence *packets*; only `ship-readiness-orchestrator` promotes claims and issues a readiness verdict, and only after `ship-deep-review`'s verifier gate.

## Preserve the safety and evidence rules verbatim

These are not stylistic — they are why the tool can be trusted:

- **Evidence grading** (confirmed / strong / provisional / needs-proof / blocked / avoided / rejected) and **coverage labels** (covered / sampled / blocked / avoided / inferred / missing / out_of_scope / evidence_debt).
- **No-overclaim rule:** never emit `ready`, `works`, `secure`, `accessible`, `beloved`, `viral`, `passing`, or `fixed` without supporting evidence.
- **Safe-test boundaries:** read-only by default; never click mutating/paid/destructive/publishing/permissioned/production actions without explicit permission and a disposable environment.
- **Verifier independence:** the verifier sees raw outputs + a terse ledger, never a polished narrative.

If a change would weaken any of the above, it will not be merged, even if it makes output shorter or faster.

## Triggering is `name` + `description` — treat descriptions as an interface

Each skill auto-activates based on its `name:` and `description:` frontmatter. **Do not remove trigger keywords from a `description`.** You may append clarifying context, but existing keywords are load-bearing. If you change a skill's scope, update the description additively and note it in the PR.

## Renames are atomic

If you rename a skill, update **all** of: the folder, the `name:` frontmatter, the H1 title, every `$name` reference, every backtick `` `name` `` reference in prose, the orchestrator's "Required Sub-Skills" and "Sub-Skill Load Gate" resolution steps, and any name/path references inside `agents/*.yaml`, templates, and JSON (`coverage-map.json` has a `"skill"` field). Then re-grep every old name — the only permitted remaining hit is a labeled migration note. See [`docs/naming.md`](docs/naming.md) for how the current names were derived.

## Local checks before a PR

```bash
# 1) No stale skill-name references anywhere:
grep -rn -E '\b(product-readiness-orchestrator|audit-product-workflows|audit-workflow-clarity)\b' plugins/ && echo "STALE FOUND" || echo "clean"

# 2) Each skill's frontmatter parses and the load gate resolves to real folders:
for s in plugins/shipworthy/skills/ship-*; do test -f "$s/SKILL.md" || echo "MISSING SKILL.md in $s"; done

# 3) JSON templates are valid:
find . -name '*.json' -exec sh -c 'python3 -m json.tool "$1" >/dev/null && echo "ok $1"' _ {} \;
```

## Scope of contributions we love

- New **archetype overlays** or **reference lanes** that add evidence rigor without adding a competing verdict.
- Better **path-discovery** heuristics and **backend-symptom** detection tied to user-visible breaks.
- Real **worked examples** and demo captures (record your own — never commit a faked asciinema cast).
- Docs that make the control stack clearer.

## What to avoid

- Turning a lane into an unbounded backend/security architecture review.
- Adding a second ledger or letting a lane declare "ready."
- Screenshot-only claims about behavior, persistence, accessibility, or reachability.
- Recommending a broad redesign where a smaller fix solves the observed consequence.

By contributing, you agree your contributions are licensed under the repository's [MIT License](LICENSE).
