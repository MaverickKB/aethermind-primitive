# Grok Build Recipe

Grok Build can use AetherMind through shell commands in its task instructions or project rules.

The important behavior is not Grok-specific. Actual work should write concise continuity layers at the real project root.

## Rule fragment

```text
For project work, use AetherMind through the CLI:

1. At the real project root, run:
   aethermind init --root . --purpose "Grok Build continuity"

2. When a load-bearing decision, correction, uncertainty, friction point, or verification result appears, write:
   aethermind layer --root . --type <decision|correction|discovery|friction> --ctx <context> --body <dense durable content>

3. Use validate/status/inspect only as diagnostic checks.

4. For remote/customer systems, use aethermind remote-note so continuity is kept locally by default.

Do not dump transcripts, secrets, routine progress logs, generated evidence, or unrelated operator context into layers.
```

## Example

```bash
aethermind layer \
  --root . \
  --type decision \
  --ctx agent-rules/continuity \
  --body "Use the AetherMind CLI directly from Grok Build rules; do not require a Grok-specific adapter for v0.1.0"
```

## Remote/customer systems

```bash
aethermind remote-note \
  --remote customer-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Captured durable incident context locally; no remote .aethermind store written"
```
