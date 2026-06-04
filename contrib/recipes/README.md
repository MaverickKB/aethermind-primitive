# Integration Recipes

These recipes show how common agent runners can use AetherMind through the CLI.

They are examples, not core architecture. The primitive is the AEM format plus the write-capable CLI/reference library. Agent-specific instructions belong here only when they help an agent remember to write useful layers at the right moments.

A good recipe should tell the runner to:

1. initialize the store at the real project or data root;
2. write layers for load-bearing decisions, corrections, friction, uncertainty, and verification;
3. use diagnostic commands only for checking state;
4. use `remote-note` for remote/customer systems by default;
5. avoid dumping transcripts, secrets, generated evidence, or routine progress logs into layers.
