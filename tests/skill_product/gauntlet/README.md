# Exhaustive Surface Gauntlet

This repository-only acceptance fixture measures whether the four Shipworthy
skills discover and honestly close a finite adversarial product surface. It is
not installed with the skills and does not launch agents.

`run_acceptance.py prepare` requires `--skills-revision`, materializes the four
skills from that Git commit, starts the localhost fixture, and records bounded
skill/fixture/prompt/comparator/oracle fingerprints. The Codex macOS coordinator
launches a fresh native Codex test subject. `finalize` validates its three
required artifacts, compares the frontier with the private oracle, retains the
controller receipt for reproducible rescoring after the subject exits, cleans
transient state, and atomically writes the authoritative result. `cleanup` is
idempotent recovery.

The isolation claim is procedural because native agents share filesystem
capability. Claude, provider calls, external network access, and real installed
skill writes are outside this harness.
