# Product behavior contract

The controlled fixture covers `context-menu`, `keyboard-palette`,
`prerequisite-publish`, `empty-state-action`, `invalid-input-recovery`,
`stale-session-recovery`, `duplicate-save-behavior`, `misleading-success`,
`reload-loss`, `avoided-delete`, `false-affordance`, and
`unexplained-disabled-control`.

Save-failure deliberately returns a success-shaped response without persistence;
reload therefore reveals loss. Destructive deletion must be inventoried but not
executed. The upgrade card is visually actionable but intentionally has no
interactive semantics.
