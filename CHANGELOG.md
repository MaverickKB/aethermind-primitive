# Change log

## 0.2.0

### Continuity methods

- Added artifact-reference, anchor, pressure-event, supersession, and rollback
  primitives alongside the base layer primitive.
- Added currentness projection, scoped briefs, anchor briefs, filtered reads, and
  explicit capability reporting.
- Added canonical texture writes, routine events in `events.aem`, and archival
  records in `archive.aem`.
- Added correction links, thread heads, evidence, recurrence, verification, artifact
  references, and anchor fields.
- Added explicit store initialization.

### Compatibility

- Preserved the 0.1 root-first Python API.
- Preserved the `init`, `layer`, `validate`, `status`, `inspect`,
  `export`, `import`, and `remote-note` command names.
- Preserved the original key/value output and opt-in `--json` output for those
  commands, including fresh-store initialization through `layer`.
- Kept 0.1 `layers.aem` records readable, including UUID IDs,
  `schema_version = "aem-v1"`, and remote-work fields.
- New records append after existing records without rewriting prior bytes.
- Imports validate before replacement and preserve a durable, uniquely named
  backup when the target store changes.

### Documentation

- Updated the format reference for all six Light v1 primitives.
- Added an explicit 0.1 to 0.2 upgrade and rollback path.
- Updated the quickstart and examples for the current methods.
