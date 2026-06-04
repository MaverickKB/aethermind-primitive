# AetherMind

AetherMind is an open source continuity primitive for AI-assisted work.

It gives agents a small, shared way to preserve load-bearing context beside the project they are changing: decisions, corrections, uncertainty, friction, and verification that should survive the current chat or agent run.

It is not a transcript store, task log, project manager, or hosted memory service.

## Why it exists

AI coding agents lose useful working judgment across context limits, handoffs, fresh sessions, and tool boundaries. AetherMind records that judgment as append-only layers in a project-local `.aethermind/` store.

Any agent that can run shell commands can use it.

## Quickstart

```bash
aethermind init --root . --purpose "start project continuity"
aethermind layer --root . --type decision --ctx build --body "Use the CLI as the universal v0.1.0 surface"
aethermind validate --root .
```

`init` creates `.aethermind/` and writes an init layer. `layer` records durable work context. `validate`, `status`, and `inspect` are diagnostic commands; they are not a substitute for writing continuity during real work.

## Remote/customer work

For work on systems where you should not leave project artifacts by default, write local remote-work continuity:

```bash
aethermind remote-note \
  --remote customer-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Inspected service state; kept continuity locally"
```

The remote target is metadata. The note is stored locally under a remote-work store and does not create `.aethermind/` on the remote/customer system by default.

## Agent recipes

Basic recipes for Codex, Claude Code, and Grok Build live under `contrib/recipes/`. They are examples of using the CLI from agent runners; they are not separate architectures.

## Scope

See `SCOPE.md` for the product boundary and what belongs in an AetherMind layer.
