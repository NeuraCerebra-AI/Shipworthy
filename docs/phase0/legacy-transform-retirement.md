# Legacy transform retirement criteria

The legacy reporting transforms remain compatibility resources. Repository-only
dual-render comparison does not change any skill trigger or the mandatory
`readiness-report.html` contract.

Retirement is allowed only after all six criteria below are evidenced together:

1. The legacy and v1 paths have coexisted for **two supported releases**.
2. Supported fixtures and production-approved samples show **zero unexplained dual-render differences**.
   Explained changes stay in the comparison record;
   unexplained changes remain evidence debt.
3. The compatibility data has completed **successful export and restore**, with
   exact integrity evidence for the restored state.
4. Repository skill files and every supported synthetic client fixture have exact **installed-copy parity**,
   including skill bodies, scripts, references, templates, and host manifests.
5. Every known downstream consumer has a **documented consumer migration**,
   including its accepted schema/producer versions and rollback route.
6. **Raw legacy import remains supported or is explicitly version-gated** with bounded diagnostics and a documented recovery route.

No single release, passing renderer snapshot, or installer observation can waive
another criterion. Evidence must name the supported releases, fixture inventory,
export/restore digest, parity report, migrated consumers, and applicable legacy
input versions.

Phase 1 is not started by this work. These criteria authorize neither a public
CLI workflow nor persistence, runners, services, portals, providers, or installed
copy changes.
