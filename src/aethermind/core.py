from __future__ import annotations

import re
import tomllib
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

FORMAT_VERSION = "aem-v1"
REQUIRED_FIELDS = {
    "id",
    "ts",
    "author",
    "type",
    "body",
    "ctx",
    "conf",
    "markers",
    "primitive",
    "schema_version",
}


def _store_for_root(root: str | Path) -> Path:
    path = Path(root).expanduser()
    if path.name == ".aethermind":
        return path
    return path / ".aethermind"


def _layers_file(root: str | Path) -> Path:
    return _store_for_root(root) / "layers.aem"


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _toml_string(value: str) -> str:
    return "\"" + value.replace("\\", "\\\\").replace('"', '\\"') + "\""


def _toml_list(values: list[str]) -> str:
    return "[" + ", ".join(_toml_string(str(value)) for value in values) + "]"


def _as_list(value: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _format_value(value: Any) -> str:
    if isinstance(value, list):
        return _toml_list([str(item) for item in value])
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return _toml_string(str(value))


def _serialize_layer(layer: dict[str, Any]) -> str:
    preferred = [
        "id",
        "ts",
        "author",
        "type",
        "ctx",
        "conf",
        "markers",
        "primitive",
        "schema_version",
        "body",
        "evidence",
        "next",
        "verification",
        "remote_target",
        "local_store_reason",
        "source_tool",
        "store_kind",
    ]
    lines = ["[[layer]]"]
    seen: set[str] = set()
    for key in preferred:
        if key in layer and (key in REQUIRED_FIELDS or layer[key] not in (None, [], "")):
            lines.append(f"{key} = {_format_value(layer[key])}")
            seen.add(key)
    for key in sorted(set(layer) - seen):
        if layer[key] not in (None, [], ""):
            lines.append(f"{key} = {_format_value(layer[key])}")
    return "\n".join(lines) + "\n\n"


def _load_raw(root: str | Path) -> dict[str, Any]:
    path = _layers_file(root)
    if not path.exists():
        return {"layer": []}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid AEM store: {exc}") from exc


def _check_layer(layer: dict[str, Any], seen_ids: set[str]) -> str | None:
    missing = sorted(REQUIRED_FIELDS - set(layer))
    if missing:
        return f"missing required fields: {', '.join(missing)}"
    if layer["schema_version"] != FORMAT_VERSION:
        return f"unsupported schema_version: {layer['schema_version']}"
    if layer["id"] in seen_ids:
        return f"duplicate layer id: {layer['id']}"
    seen_ids.add(str(layer["id"]))
    if not isinstance(layer["markers"], list):
        return "markers must be a list"
    if not 0 <= float(layer["conf"]) <= 1:
        return "conf must be between 0.0 and 1.0"
    return None


def validate_store(root: str | Path) -> dict[str, Any]:
    try:
        raw = _load_raw(root)
    except ValueError as exc:
        return {"ok": False, "errors": [str(exc)], "layer_count": 0}
    layers = raw.get("layer", [])
    errors: list[str] = []
    seen: set[str] = set()
    for layer in layers:
        error = _check_layer(layer, seen)
        if error:
            errors.append(error)
    return {"ok": not errors, "errors": errors, "layer_count": len(layers)}


def read_layers(root: str | Path) -> list[dict[str, Any]]:
    validation = validate_store(root)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    return list(_load_raw(root).get("layer", []))


def export_store(root: str | Path, destination: str | Path) -> dict[str, Any]:
    validation = validate_store(root)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    dest = Path(destination).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    source = _layers_file(root)
    dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return {"ok": True, "file": str(dest), "layer_count": validation["layer_count"]}


def import_layers(root: str | Path, source_file: str | Path) -> dict[str, Any]:
    source = Path(source_file).expanduser()
    text = source.read_text(encoding="utf-8")
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid import file: {exc}") from exc
    layers = raw.get("layer", [])
    store = _store_for_root(root)
    store.mkdir(parents=True, exist_ok=True)
    target = store / "layers.aem"
    target.write_text(text, encoding="utf-8")
    validation = validate_store(root)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    return {"ok": True, "store": str(store), "imported_layers": len(layers), "layer_count": validation["layer_count"]}


def _append_layer(root: str | Path, layer: dict[str, Any]) -> dict[str, Any]:
    store = _store_for_root(root)
    store.mkdir(parents=True, exist_ok=True)
    path = store / "layers.aem"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(_serialize_layer(layer))
    validation = validate_store(root)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    return {"ok": True, "store": str(store), "layer_id": layer["id"], "layer_count": validation["layer_count"]}


def write_layer(
    root: str | Path,
    *,
    type: str,
    body: str,
    ctx: str,
    author: str = "aethermind-cli",
    conf: float = 1.0,
    markers: str | list[str] | None = None,
    evidence: str | list[str] | None = None,
    next: str | list[str] | None = None,
    verification: str | list[str] | None = None,
    remote_target: str | None = None,
    local_store_reason: str | None = None,
    source_tool: str | None = None,
    store_kind: str = "local",
) -> dict[str, Any]:
    layer = {
        "id": str(uuid.uuid4()),
        "ts": _now(),
        "author": author,
        "type": type,
        "body": body,
        "ctx": ctx,
        "conf": conf,
        "markers": _as_list(markers),
        "primitive": "layer",
        "schema_version": FORMAT_VERSION,
        "evidence": _as_list(evidence),
        "next": _as_list(next),
        "verification": _as_list(verification),
        "remote_target": remote_target,
        "local_store_reason": local_store_reason,
        "source_tool": source_tool,
        "store_kind": store_kind,
    }
    return _append_layer(root, layer)


def init_store(root: str | Path, *, purpose: str, author: str = "aethermind-cli") -> dict[str, Any]:
    store = _store_for_root(root)
    store.mkdir(parents=True, exist_ok=True)
    (store / "texture.aem").touch(exist_ok=True)
    if _layers_file(root).exists() and read_layers(root):
        return {"ok": True, "store": str(store), "already_initialized": True}
    return write_layer(root, type="init", ctx="aethermind/init", body=purpose, author=author, markers=["!"], source_tool="aethermind-cli")


def safe_target_name(remote_target: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", remote_target.strip()).strip(".-_")
    return safe or "remote-target"


def remote_note(
    *,
    remote_target: str,
    task: str,
    ctx: str,
    body: str,
    notes_root: str | Path | None = None,
    author: str = "aethermind-cli",
    evidence: str | list[str] | None = None,
    markers: str | list[str] | None = None,
) -> dict[str, Any]:
    base = Path(notes_root).expanduser() if notes_root else Path.home() / ".aethermind" / "remote-work"
    local_root = base / safe_target_name(remote_target) / safe_target_name(task)
    local_root.mkdir(parents=True, exist_ok=True)
    result = write_layer(
        local_root,
        type="remote-work",
        ctx=ctx,
        body=body,
        author=author,
        markers=_as_list(markers) or ["!"],
        evidence=evidence,
        remote_target=remote_target,
        local_store_reason="remote/customer continuity is stored locally by default to avoid leaving AetherMind artifacts on the remote system",
        source_tool="aethermind-cli",
        store_kind="remote-work",
    )
    result["remote_target"] = remote_target
    result["local_root"] = str(local_root)
    return result
