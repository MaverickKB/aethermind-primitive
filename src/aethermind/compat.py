"""Compatibility surface for the public 0.1 API.

The continuity engine lives in :mod:`aethermind.core`. This module preserves
the original root-first helpers while routing all writes through that engine.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from . import core


def _store_for_root(root: str | Path) -> Path:
    path = Path(root).expanduser()
    return path if path.name == ".aethermind" else path / ".aethermind"


def _project_for_root(root: str | Path) -> Path:
    path = Path(root).expanduser()
    return path.parent if path.name == ".aethermind" else path


def _layers_file(root: str | Path) -> Path:
    return _store_for_root(root) / "layers.aem"


def _as_list(value: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _fsync_directory(path: Path) -> None:
    """Persist directory entry changes where the host supports it."""

    try:
        directory_fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _preserve_file(path: Path) -> Path:
    """Create one durable, collision-free copy beside *path*."""

    stamp = core.datetime.now(core.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    handle, backup_name = tempfile.mkstemp(
        prefix=f"{path.name}.backup-{stamp}-", dir=path.parent
    )
    backup_path = Path(backup_name)
    try:
        with os.fdopen(handle, "wb") as backup, path.open("rb") as source:
            shutil.copyfileobj(source, backup)
            backup.flush()
            os.fsync(backup.fileno())
        shutil.copystat(path, backup_path)
        _fsync_directory(path.parent)
    except Exception:
        backup_path.unlink(missing_ok=True)
        raise
    return backup_path


def validate_store(root: str | Path) -> dict[str, Any]:
    path = _layers_file(root)
    if not path.exists():
        return {"ok": True, "errors": [], "layer_count": 0}
    report = core.LayerStore(path).read_report()
    errors = [
        f"record {issue.record_index} at byte {issue.byte_offset}: {issue.message}"
        for issue in report.issues
    ]
    return {"ok": not errors, "errors": errors, "layer_count": len(report.layers)}


def read_layers(root: str | Path) -> list[dict[str, Any]]:
    validation = validate_store(root)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    path = _layers_file(root)
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    data = core.tomllib.loads(path.read_text(encoding="utf-8"))
    layers = data.get("layer", data.get("layers", []))
    return list(layers) if isinstance(layers, list) else []


def export_store(root: str | Path, destination: str | Path) -> dict[str, Any]:
    validation = validate_store(root)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    source = _layers_file(root)
    dest = Path(destination).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())
    return {"ok": True, "file": str(dest), "layer_count": validation["layer_count"]}


def import_layers(root: str | Path, source_file: str | Path) -> dict[str, Any]:
    """Import a validated AEM file while preserving any replaced store."""

    source = Path(source_file).expanduser()
    payload = source.read_bytes()
    with tempfile.TemporaryDirectory(prefix="aethermind-import-check-") as tmp:
        candidate = Path(tmp) / "layers.aem"
        candidate.write_bytes(payload)
        report = core.LayerStore(candidate).read_report()
        if report.issues:
            issue = report.issues[0]
            raise ValueError(
                f"invalid import record {issue.record_index} "
                f"at byte {issue.byte_offset}: {issue.message}"
            )

    store = _store_for_root(root)
    store.mkdir(parents=True, exist_ok=True)
    target = store / "layers.aem"
    backup: str | None = None
    if target.exists() and target.read_bytes() != payload:
        backup = str(_preserve_file(target))

    handle, temporary_name = tempfile.mkstemp(prefix=".layers.aem.", dir=store)
    try:
        with os.fdopen(handle, "wb") as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, target)
        _fsync_directory(store)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)

    return {
        "ok": True,
        "store": str(store),
        "imported_layers": len(report.layers),
        "layer_count": len(report.layers),
        "backup": backup,
    }


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
    store_kind: str | None = "local",
    primitive: str = "layer",
    **fields: Any,
) -> dict[str, Any]:
    if isinstance(conf, bool) or not isinstance(conf, (int, float)):
        raise ValueError("conf must be a number, not bool or another scalar type")
    aether = core.AetherMind(_project_for_root(root), create=True)
    layer = aether.write_layer(
        type=type,
        body=body,
        ctx=ctx,
        author=author,
        conf=float(conf),
        markers=_as_list(markers),
        evidence=_as_list(evidence),
        next=_as_list(next),
        verification=_as_list(verification),
        remote_target=remote_target,
        local_store_reason=local_store_reason,
        source_tool=source_tool,
        store_kind=store_kind,
        primitive=primitive,
        **fields,
    )
    return {
        "ok": True,
        "store": str(aether.aethermind_dir),
        "layer_id": layer.id,
        "layer_count": len(aether.read_layers()),
        "receipt_hash": getattr(layer, "receipt_hash", None),
    }


def init_store(
    root: str | Path,
    *,
    purpose: str,
    author: str = "aethermind-cli",
) -> dict[str, Any]:
    aether = core.AetherMind(_project_for_root(root), create=True)
    aether.texture_path.touch(exist_ok=True)
    existing = aether.read_layers()
    if existing:
        return {
            "ok": True,
            "store": str(aether.aethermind_dir),
            "already_initialized": True,
        }
    return write_layer(
        root,
        type="init",
        ctx="aethermind/init",
        body=purpose,
        author=author,
        markers=["!"],
        source_tool="aethermind-cli",
    )


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
    base = (
        Path(notes_root).expanduser()
        if notes_root
        else Path.home() / ".aethermind" / "remote-work"
    )
    local_root = base / safe_target_name(remote_target) / safe_target_name(task)
    result = write_layer(
        local_root,
        type="remote-work",
        ctx=ctx,
        body=body,
        author=author,
        markers=_as_list(markers) or ["!"],
        evidence=evidence,
        remote_target=remote_target,
        local_store_reason=(
            "remote continuity is stored locally by default so the remote "
            "filesystem is unchanged"
        ),
        source_tool="aethermind-cli",
        store_kind="remote-work",
    )
    result["remote_target"] = remote_target
    result["local_root"] = str(local_root)
    return result
