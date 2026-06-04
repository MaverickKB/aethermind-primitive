# Privacy

AetherMind stores are project data.

A layer can contain sensitive context if an agent writes sensitive context into it. Treat `.aethermind/` like logs, notes, transcripts, crash reports, and generated diagnostics: useful locally, but not automatically safe to publish.

## Before sharing a repository

Review whether the repository includes `.aethermind/` and whether those layers belong in the shared artifact.

For public repositories, the safer default is to exclude local `.aethermind/` stores unless the project explicitly intends to publish those layers.

## What not to write

Do not put secrets, credentials, private customer details, unrelated session notes, or generated evidence dumps into layers.

A good layer records the durable judgment a future agent needs. It should not turn the project into a transcript archive or low-signal note dump.

## Remote/customer systems

For remote/customer work, use `aethermind remote-note` by default. It records continuity locally and treats the remote target as metadata, so the primitive does not leave `.aethermind/` artifacts on systems where persistence policy may be different.
