# Upgrading to AetherMind 0.2

AetherMind 0.2 reads existing 0.1 `layers.aem` files directly. The upgrade does
not require a store rewrite.

## Before installing

Preserve the project-local store using the same versioning or backup method used for
the project:

```bash
cp -R .aethermind .aethermind.pre-0.2
```

If `.aethermind/` is already versioned with the project, a clean source-control
commit provides the same rollback point.

## Install and verify

```bash
python -m pip install .
aethermind validate --root .
aethermind status --project-root .
```

A valid 0.1 store reports its existing layer count. No files are rewritten by these
read commands.

## Continue writing

The original command remains valid:

```bash
aethermind layer \
  --root . \
  --type discovery \
  --ctx upgrade/verification \
  --body "AetherMind 0.2 reads the existing store"
```

The new record is appended after the existing bytes. UUID IDs from 0.1 and numeric
IDs from 0.2 can coexist.

## Import behavior

`aethermind import --root . --file incoming.aem` validates the complete incoming
file before replacing `layers.aem`. If the target differs, the command first
creates a collision-free
`layers.aem.backup-<UTC timestamp>-<unique suffix>` file in the same store.

## Rollback

To return to the preserved store:

```bash
mv .aethermind .aethermind.from-0.2
mv .aethermind.pre-0.2 .aethermind
```

Keep `.aethermind.from-0.2` until any new 0.2 records have been reviewed and
carried forward.
