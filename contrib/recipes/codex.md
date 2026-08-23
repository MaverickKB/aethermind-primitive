# Codex Recipe

Codex can use AetherMind through the installed CLI.

Use it at the real project root, not the user home directory or an unrelated launch directory.

## Start work

```bash
aethermind init --root . --purpose "Codex continuity"
```

## Record durable context

Write a layer when Codex makes or discovers something future runs should not flatten:

```bash
aethermind layer \
  --root . \
  --type decision \
  --ctx build/cli \
  --body "Use the package CLI rather than a runner-specific adapter"
```

Good Codex layer triggers:

- a decision and the reason it won;
- a corrected assumption;
- a test or verification result that changes confidence;
- a failure mode future Codex runs should not repeat;
- an unresolved uncertainty that affects the next step.

Do not write routine progress summaries, full transcripts, credentials, or
unrelated release-process chatter into project layers.

## Remote/customer systems

Use `aethermind remote-note` so continuity is kept locally by default:

```bash
aethermind remote-note \
  --remote customer-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Observed service restart loop; kept continuity locally"
```
