# Exhaustive Surface Gauntlet

This repository-only acceptance fixture measures whether the four Shipworthy
skills discover and honestly close a finite adversarial product surface. It is
not installed with the skills and does not launch agents.

`run_acceptance.py prepare` starts the localhost fixture and creates isolated
copied inputs. The Codex macOS coordinator launches a fresh native Codex test
subject. `finalize` validates its three required artifacts, compares the
frontier with the private oracle, cleans transient state, and atomically writes
the authoritative result. `cleanup` is idempotent recovery.

The isolation claim is procedural because native agents share filesystem
capability. Claude, provider calls, external network access, and real installed
skill writes are outside this harness.
