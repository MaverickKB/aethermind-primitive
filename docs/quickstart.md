# Quickstart

This quickstart assumes the `aethermind` CLI is installed and available on `PATH`.

## Start local project continuity

From the project or data root you are working on:

```bash
aethermind init --root . --purpose "start project continuity"
```

This creates `.aethermind/` beside the work root and writes an init layer.

## Write a work layer

When the session produces a load-bearing decision, correction, discovery, failure mode, or verification result, write it as a layer:

```bash
aethermind layer \
  --root . \
  --type decision \
  --ctx build/cli \
  --body "Use the CLI as the universal v0.1.0 surface"
```

Keep layers dense. They should help a future agent act with better judgment, not replay the whole session.

## Check the store

```bash
aethermind validate --root .
aethermind status --root .
aethermind inspect --root .
```

These commands are diagnostic. They do not replace writing layers during real work.

## Remote/customer work

For work on a remote or customer system, write local remote-work continuity by default:

```bash
aethermind remote-note \
  --remote customer-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Inspected service state; continuity kept locally"
```

This writes under a local remote-work store such as `~/.aethermind/remote-work/...` and does not create `.aethermind/` on the remote/customer target by default.

Use this when the continuity is useful to the operator but the remote system should not receive new persistence artifacts.
