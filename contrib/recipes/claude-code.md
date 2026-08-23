# Claude Code Recipe

Claude Code can use AetherMind through the installed CLI.

Use it at the real project root so `.aethermind/` sits beside the source or data being changed.

## Start work

```bash
aethermind init --root . --purpose "Claude Code continuity"
```

## Record durable context

Write a layer when Claude Code produces a decision, correction, discovery, uncertainty, friction point, or verification result that future runs need:

```bash
aethermind layer \
  --root . \
  --type correction \
  --ctx docs/scope \
  --body "Scope docs should state product boundaries, not session history"
```

Keep the layer dense. The point is continuity, not a report.

Avoid writing:

- secrets or customer-identifying details;
- copied chat transcripts;
- generated output dumps;
- routine status logs;
- unrelated local operator context.

## Remote/customer systems

For remote/customer work, write local remote-work continuity by default:

```bash
aethermind remote-note \
  --remote customer-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Inspected service state; no remote persistence written"
```
