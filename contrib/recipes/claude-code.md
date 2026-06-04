# Claude Code Recipe

Claude Code can use AetherMind through the installed CLI.

Start work:

```bash
aethermind init --root . --purpose "Claude Code continuity"
```

Record durable work context:

```bash
aethermind layer --root . --type decision --ctx build --body "Load-bearing decision here"
```

For remote/customer systems, use `aethermind remote-note` so continuity is kept locally by default.
