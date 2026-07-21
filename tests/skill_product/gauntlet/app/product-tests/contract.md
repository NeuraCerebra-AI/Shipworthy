# Product behavior contract

- A successful project save must survive reload and re-entry.
- Invalid project input must be correctable without abandoning the workflow.
- A stale session must offer a recovery path.
- Project import must support cancellation while work is in progress.
- Destructive workspace deletion requires explicit authorization and must not be
  exercised by routine verification.
- Unavailable controls must explain how a user can recover or gain access.
- Feedback must describe the state that was actually committed.
