# Quickstart

## Install

```bash
python -m pip install .
```

## Initialize a project store

```bash
aethermind init --root . --purpose "start project continuity"
```

This creates `.aethermind/`, writes the first layer, and leaves the 0.1 command
shape intact. The 0.2 directory-only initialization form is:

```bash
aethermind init --project-root .
```

That form creates the store directory without adding continuity. Use the
purpose form when beginning real work so the store starts with a meaningful
layer.

## Write continuity

```bash
aethermind write-layer \
  --project-root . \
  --type decision \
  --ctx build/adapter \
  --body "Use the host that owns the project filesystem" \
  --marker "!"
```

The original alias remains valid:

```bash
aethermind layer \
  --root . \
  --type discovery \
  --ctx build/adapter \
  --body "The original command still works"
```

## Read and orient

```bash
aethermind read-layers --project-root .
aethermind currentness --project-root .
aethermind brief --project-root .
aethermind brief-anchor --project-root . --anchor aem-example
```

`inspect --root .` remains an alias for `read-layers`.

## Record texture and routine events

```bash
aethermind write-texture \
  --project-root . \
  --ctx build/attention \
  --body "Keep the adapter thin"

aethermind write-event \
  --project-root . \
  --type observation \
  --ctx build/run \
  --body "Local smoke completed"
```

## Check the store

```bash
aethermind validate --root .
aethermind status --project-root .
aethermind audit --project-root .
aethermind capabilities --project-root .
```

## Upgrade an existing store

No rewrite is required for a 0.1 `layers.aem` file. Install 0.2 and validate it:

```bash
aethermind validate --root .
aethermind status --project-root .
```

The first new write appends a 0.2 record after the existing records. See
[Upgrading to 0.2](upgrading-to-0.2.md) for preservation and rollback steps.
