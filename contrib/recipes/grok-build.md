# Grok Build Recipe

Use the CLI from a Grok Build task when work starts and whenever a load-bearing decision, correction, or verification result is produced.

Example prompt/rule fragment:

```text
For actual project work, write AetherMind layers with:
aethermind init --root . --purpose "Grok Build continuity"
aethermind layer --root . --type decision --ctx <context> --body <durable decision>
```

Remote/customer work should use `aethermind remote-note` with a local notes root if needed.
