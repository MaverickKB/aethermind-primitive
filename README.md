# AetherMind

AetherMind is an open source continuity primitive for AI-assisted work.

It preserves compact working judgment beside the project it describes: decisions,
corrections, discoveries, uncertainty, friction, verification, and the relationships
that make those records current or historical.

## Install

```bash
python -m pip install .
```

The package installs the `aethermind` command and the `aethermind` Python module.

## Quickstart

The original 0.1 commands remain available:

```bash
aethermind init --root . --purpose "start project continuity"
aethermind layer --root . --type decision --ctx build --body "Keep continuity beside the project"
aethermind validate --root .
aethermind inspect --root .
```

The 0.2 command names expose the complete local runtime:

```bash
aethermind write-layer --project-root . --type discovery --ctx build --body "The adapter path is working"
aethermind currentness --project-root .
aethermind brief --project-root .
aethermind capabilities --project-root .
```

## Store layout

AetherMind continuity uses `.aem` files inside the project-local
`.aethermind/` directory:

```text
.aethermind/
  layers.aem
  texture.aem
  events.aem
  archive.aem
```

`layers.aem` is the decision ledger. `texture.aem` holds compact attention
pointers. `events.aem` keeps routine observations separate from the decision
ledger. `archive.aem` preserves archived record copies; `layers.aem` receives
the append-only tombstone that makes the archived records historical.

## What changed in 0.2

AetherMind 0.2 extends the original primitive with the following continuity
methods:

- six supported primitives: `layer`, `artifact-reference`, `anchor`,
  `pressure-event`, `supersession`, and `rollback`;
- explicit store initialization and acknowledged append results;
- filtered reads, currentness projection, scoped briefs, and anchor briefs;
- append-only texture, event, and archive stores;
- correction, supersession, rollback, evidence, recurrence, verification, and
  artifact relationships;
- the original 0.1 Python helpers and CLI command names.

Existing 0.1 `layers.aem` files remain readable. New records append without
rewriting existing records. See [Upgrading to 0.2](docs/upgrading-to-0.2.md).

## Python

The 0.1 root-first API remains available:

```python
from aethermind import init_store, read_layers, validate_store, write_layer

init_store(".", purpose="start project continuity")
write_layer(
    ".",
    type="decision",
    ctx="build/runtime",
    body="Use the project-local AEM store.",
    markers=["!"],
)
layers = read_layers(".")
status = validate_store(".")
```

The current engine is available through `AetherMind`:

```python
from aethermind import AetherMind

store = AetherMind(".", create=False)
brief = store.brief()
current = store.currentness()
```

## Remote work

`aethermind remote-note` writes continuity to a local remote-work store while
recording the target as metadata:

```bash
aethermind remote-note \
  --remote example-host:/srv/app \
  --task incident-1 \
  --ctx triage \
  --body "Inspected the service and retained the decision locally"
```

## Documentation

- [Scope](SCOPE.md)
- [AEM format](spec/AEM_FORMAT.md)
- [Quickstart](docs/quickstart.md)
- [Upgrading to 0.2](docs/upgrading-to-0.2.md)
- [Change log](CHANGELOG.md)
- [Privacy](docs/privacy.md)
