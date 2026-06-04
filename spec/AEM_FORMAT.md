# AEM Format v1

AEM v1 is an append-friendly layer format for AetherMind stores.

## Store layout

A local store lives at:

```text
<work-root>/.aethermind/
  layers.aem
  texture.aem       # optional
```

Remote/customer work uses a local store described in `spec/REMOTE_WORK.md`.

## Normative layer fields

Each layer is a TOML table named `[[layer]]` with these required fields:

- `id`: stable unique string within the store.
- `ts`: UTC timestamp string in ISO-8601 form.
- `author`: tool, harness, or agent writing the layer.
- `type`: short layer type such as `decision`, `discovery`, `correction`, `friction`, or `init`.
- `body`: concise durable content.
- `ctx`: context path such as `build/cli`.
- `conf`: numeric confidence from 0.0 to 1.0.
- `markers`: list of semantic marker strings.
- `primitive`: for v0.1.0, normally `layer`.
- `schema_version`: `aem-v1`.

Optional fields:

- `evidence`: list of evidence strings.
- `next`: list of next-action strings.
- `verification`: verification string or list.
- `remote_target`: metadata identifying a remote/customer target.
- `local_store_reason`: reason continuity was written locally instead of remotely.
- `source_tool`: writing tool or harness.
- `store_kind`: `local` or `remote-work`.

## Semantics

AEM records load-bearing continuity for future agents. The format does not require Python. The Python package is a reference implementation, not the source of truth.
