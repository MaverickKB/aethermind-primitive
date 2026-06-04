# Remote Work Stores

Remote/customer actual work still writes AetherMind layers, but by default those layers are written locally rather than onto the remote/customer system.

Default local notes root:

```text
~/.aethermind/remote-work/<safe-target>/<task>/.aethermind/
```

Rules:

1. `remote_target` is metadata, not a filesystem destination.
2. The default implementation must not create `.aethermind/` under the remote/customer path.
3. Safe target directory names are sanitized from the remote target string.
4. Remote-work layers include `remote_target`, `store_kind = "remote-work"`, and `local_store_reason`.
5. Users may choose other local notes roots, but the layer must still identify the remote target and local-store reason.

This keeps continuity for the operator without leaving AetherMind artifacts on systems where that may be inappropriate.
