# AetherMind

AetherMind is a universal, harness-free open source continuity primitive for agent work.

The v0.1.0 path is simple:

```bash
aethermind init --root . --purpose "start project continuity"
aethermind layer --root . --type decision --ctx build --body "Use the CLI as the universal v0.1.0 surface"
aethermind validate --root .
```

Any agent that can execute shell commands can write AetherMind layers.

For remote/customer work:

```bash
aethermind remote-note --remote customer-host:/srv/app --task incident-1 --ctx triage --body "Inspected service state; kept continuity locally"
```

That writes local remote-work continuity and does not leave `.aethermind/` on the remote/customer system by default.
