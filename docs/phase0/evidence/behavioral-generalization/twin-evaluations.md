# Counterfactual twin evaluations

Evaluation revision: `5976f89639b6c1cbeb338e451662814e9f762932`

Subjects: eight fresh native Codex agents, one oracle-blind runtime-only subject per opaque endpoint

Fixture root: temporary and controller-private; no installed-copy writes

Each pair used the same parameterized application and differed in exactly one
declared behavior. The subject saw only endpoint labels `A` or `B`, the copied
four skills, the bounded brief, the localhost application, and its output
directory. The variant mapping, comparator, oracle, controller receipt, other
endpoint, repository, and prior observations were outside the allowlist.

| Pair | Defective endpoint | Corrected endpoint | Behavioral result | Acceptance |
|---|---|---|---|---|
| Save persistence | A found `save-success-without-reentry-persistence`; direct re-entry restored `Alpha` after the primary Save claimed success. | B proved the primary Save survived re-entry and did not report that defect. | Correct sensitivity to the controlled primary-Save persistence delta. The unrelated secondary Save defect remained observable on both sides and was not required to use identical wording. | PASS |
| Disabled recovery | A reported disabled Archive with no visible recovery explanation. | B observed `Ask a workspace owner to enable project archiving` and did not report the missing-recovery defect. | Correct sensitivity to the sole explanation delta. | PASS |
| Keyboard command existence | A discovered and exercised Control/Command+K and recorded the spawned Quick actions dialog. | B did not claim that the command existed, but its bounded negative probe did not explicitly record Control/Command+K as an attempted no-op. | Presence sensitivity is correct; corrected-side absence proof is incomplete. | REVIEW_REQUIRED |
| Success versus failure feedback | A reported false success from the primary Save before re-entry disproved persistence. | B observed truthful `Save failed` feedback for the primary Save and did not report a primary-Save false-success defect. | Correct sensitivity to the controlled feedback delta. The independent secondary Save false success remained a valid unrelated finding. | PASS |

No pair claimed exhaustive product closure. Destructive controls were avoided.
Unrelated findings were evaluated semantically rather than required to be
textually identical. The keyboard result is preserved as an execution-proof
limitation rather than silently upgraded to PASS.

## Raw observation hashes

| Endpoint | SHA-256 |
|---|---|
| `v-persistence-a` | `f977bc080c495a2b88c5c145d4c29f9b9ae92bf5bc23ef4f83c3c3f971ac0756` |
| `v-persistence-b` | `4b7f1617f4d0d90371561b4ee2caa694da881142496562328e5d346e8b903e46` |
| `v-disabled-a` | `ccbae6f8c8a83eab1685b2e6100c3eb8d29d2b025da7fb1773904437131c9522` |
| `v-disabled-b` | `f24a5899629781756038eb8b616e2ff97e512ed9c5de77706896eb63ac75b6e0` |
| `v-keyboard-a` | `55b3c5c4279698dcedc8462936b0823b9addbcec339084ad6e289663034d8755` |
| `v-keyboard-b` | `d6b46f22170503b082f56bad82234bfa9be17fda1398681d24645ff19154c4af` |
| `v-feedback-a` | `97f76e994c6cb4b8d8b8156aa073da3a2a4f2202d4da3427467ba565b20b0abb` |
| `v-feedback-b` | `a9e3454bd6cafe4ae49a8c218b38c947d3c54c69c6be1c4849e8705b09187e8c` |

The raw observations remain development evidence only. Their private runtime
receipts and variant truth were never exposed to the subjects.
