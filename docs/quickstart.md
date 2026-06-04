# Quickstart

Install the package, then write continuity immediately.

```bash
aethermind init --root . --purpose "start project continuity"
aethermind layer --root . --type decision --ctx build --body "The CLI is the universal v0.1.0 surface"
aethermind validate --root .
```

A work session that changes or decides something should write a layer. Diagnostic commands such as `inspect`, `status`, and `validate` are for checking stores; they are not the work path.

## Remote/customer work

```bash
aethermind remote-note \
  --remote customer-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Inspected service state; continuity kept locally"
```

This writes under `~/.aethermind/remote-work/...` and does not create `.aethermind/` on the remote/customer target by default.
