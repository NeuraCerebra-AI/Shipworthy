# Manual Install and Rollback

Prefer the host's plugin manager. The repository `install.sh` is an advanced,
explicit-target fallback for temporary or local installations. It validates all
four source skills before writing and preserves existing skills under the host's
timestamped `shipworthy-backups/` directory, outside the active skill-discovery
directory, before replacement.

If an install fails, leave the backup untouched, remove only the named incomplete
manual copy, and rename the matching backup to its original skill name. Compare
the restored tree byte-for-byte before resuming. Never delete audit ledgers,
reports, bundles, or target evidence as part of skill removal.

Automated uninstall is not implemented. Use the native plugin manager, or remove
only an explicitly named manual skill directory after direct user authorization.
