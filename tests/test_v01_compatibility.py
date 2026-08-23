from __future__ import annotations

import json
from pathlib import Path

import pytest

from aethermind import (
    export_store,
    import_layers,
    init_store,
    read_layers,
    validate_store,
    write_layer,
)
from aethermind.cli import main


LEGACY_LAYER = """[[layer]]
id = "4ef07f28-c96a-4d74-a0e2-e1ae42648b46"
ts = "2026-06-04T12:00:00Z"
author = "legacy"
type = "discovery"
ctx = "compat/v0.1"
conf = 1.0
markers = ["!"]
primitive = "layer"
schema_version = "aem-v1"
body = "Existing public stores remain readable."
next = ["append without rewriting"]
source_tool = "aethermind-cli"

"""


def test_v01_store_remains_readable_and_append_only(tmp_path: Path) -> None:
    store = tmp_path / ".aethermind"
    store.mkdir()
    layers_file = store / "layers.aem"
    layers_file.write_text(LEGACY_LAYER, encoding="utf-8")

    before = layers_file.read_bytes()
    assert validate_store(tmp_path)["ok"] is True
    assert read_layers(tmp_path)[0]["schema_version"] == "aem-v1"

    result = write_layer(
        tmp_path,
        type="decision",
        body="Use the live local primitive contract.",
        ctx="compat/v0.2",
        markers=["!"],
    )

    after = layers_file.read_bytes()
    assert after.startswith(before)
    assert result["layer_count"] == 2
    assert read_layers(tmp_path)[0]["next"] == ["append without rewriting"]
    assert read_layers(tmp_path)[1]["store_kind"] == "local"


def test_validate_missing_store_does_not_create_it(tmp_path: Path) -> None:
    project = tmp_path / "fresh"
    assert validate_store(project) == {
        "ok": True,
        "errors": [],
        "layer_count": 0,
    }
    assert not (project / ".aethermind").exists()


def test_v01_export_of_missing_store_still_fails(tmp_path: Path) -> None:
    project = tmp_path / "missing-store"
    destination = tmp_path / "export.aem"

    with pytest.raises(FileNotFoundError):
        export_store(project, destination)

    assert not project.exists()
    assert not destination.exists()


def test_v01_store_directory_root_remains_supported(tmp_path: Path) -> None:
    store = tmp_path / ".aethermind"

    init_store(store, purpose="Initialize through the original store path.")
    result = write_layer(
        store,
        type="decision",
        body="Keep the original root normalization contract.",
        ctx="compat/store-root",
    )

    assert result["layer_count"] == 2
    assert (store / "layers.aem").exists()
    assert not (store / ".aethermind").exists()


def test_v01_helper_rejects_boolean_confidence_before_creating_store(
    tmp_path: Path,
) -> None:
    project = tmp_path / "invalid-confidence"

    with pytest.raises(ValueError, match="conf must be a number"):
        write_layer(
            project,
            type="decision",
            body="Boolean confidence is not numeric confidence.",
            ctx="compat/confidence",
            conf=True,
        )

    assert not project.exists()


def test_init_preserves_existing_store(tmp_path: Path) -> None:
    store = tmp_path / ".aethermind"
    store.mkdir()
    layers_file = store / "layers.aem"
    layers_file.write_text(LEGACY_LAYER, encoding="utf-8")
    before = layers_file.read_bytes()

    result = init_store(tmp_path, purpose="Should not replace existing continuity")

    assert result["already_initialized"] is True
    assert layers_file.read_bytes() == before
    assert (store / "texture.aem").exists()


def test_import_validates_first_and_preserves_replaced_store(tmp_path: Path) -> None:
    target = tmp_path / "target"
    init_store(target, purpose="Original continuity")
    original = (target / ".aethermind" / "layers.aem").read_bytes()

    source = tmp_path / "incoming.aem"
    source.write_text(LEGACY_LAYER, encoding="utf-8")
    result = import_layers(target, source)

    backup = Path(str(result["backup"]))
    assert backup.read_bytes() == original
    assert (target / ".aethermind" / "layers.aem").read_text(encoding="utf-8") == LEGACY_LAYER

    second_source = tmp_path / "incoming-second.aem"
    second_payload = LEGACY_LAYER.replace(
        "Existing public stores remain readable.",
        "A second valid import keeps a separate rollback copy.",
    )
    second_source.write_text(second_payload, encoding="utf-8")
    second_result = import_layers(target, second_source)
    second_backup = Path(str(second_result["backup"]))
    assert second_backup != backup
    assert second_backup.read_text(encoding="utf-8") == LEGACY_LAYER
    assert (target / ".aethermind" / "layers.aem").read_text(
        encoding="utf-8"
    ) == second_payload

    invalid = tmp_path / "invalid.aem"
    invalid.write_text("[[layer]]\nid = \"broken\"\n", encoding="utf-8")
    current = (target / ".aethermind" / "layers.aem").read_bytes()
    try:
        import_layers(target, invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid import should fail")
    assert (target / ".aethermind" / "layers.aem").read_bytes() == current


def test_cli_keeps_v01_command_names(tmp_path: Path, capsys) -> None:
    code = main([
        "init",
        "--root",
        str(tmp_path),
        "--purpose",
        "CLI compatibility",
        "--json",
    ])
    assert code == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert init_payload["ok"] is True
    assert "success" not in init_payload
    assert (tmp_path / ".aethermind" / "texture.aem").exists()

    code = main([
        "layer",
        "--root",
        str(tmp_path),
        "--type",
        "discovery",
        "--ctx",
        "compat/cli",
        "--body",
        "The original command still works.",
        "--json",
    ])
    assert code == 0
    layer_payload = json.loads(capsys.readouterr().out)
    assert layer_payload["ok"] is True
    assert "success" not in layer_payload
    assert "layer" not in layer_payload
    assert layer_payload["layer_count"] == 2

    code = main(["validate", "--root", str(tmp_path), "--json"])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True

    code = main(["status", "--root", str(tmp_path), "--json"])
    assert code == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["ok"] is True
    assert status_payload["errors"] == []
    assert status_payload["layer_count"] == 2

    code = main(["inspect", "--root", str(tmp_path), "--json"])
    assert code == 0
    inspect_payload = json.loads(capsys.readouterr().out)
    assert inspect_payload["ok"] is True
    assert len(inspect_payload["layers"]) == 2


def test_cli_layer_alias_initializes_fresh_root_and_keeps_plain_output(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "fresh-cli"
    code = main(
        [
            "layer",
            "--root",
            str(project),
            "--type",
            "decision",
            "--ctx",
            "compat/cli",
            "--body",
            "The original command initializes a fresh store.",
        ]
    )

    assert code == 0
    output = capsys.readouterr().out.splitlines()
    assert output[0] == "ok: True"
    assert any(line == "layer_count: 1" for line in output)
    assert (project / ".aethermind" / "layers.aem").exists()


def test_cli_inspect_preserves_raw_v01_fields(tmp_path: Path, capsys) -> None:
    project = tmp_path / "legacy-cli"
    store = project / ".aethermind"
    store.mkdir(parents=True)
    (store / "layers.aem").write_text(LEGACY_LAYER, encoding="utf-8")

    code = main(["inspect", "--root", str(project), "--json"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["layers"][0]["schema_version"] == "aem-v1"
    assert payload["layers"][0]["next"] == ["append without rewriting"]


def test_write_layer_cli_exposes_legacy_aem_fields(tmp_path: Path, capsys) -> None:
    code = main(
        [
            "write-layer",
            "--project-root",
            str(tmp_path),
            "--create",
            "--type",
            "remote-work",
            "--ctx",
            "compat/fields",
            "--body",
            "The complete AEM field set crosses the CLI boundary.",
            "--next",
            "verify the downstream adapter",
            "--remote-target",
            "example-host:/srv/app",
            "--local-store-reason",
            "continuity remains local",
            "--source-tool",
            "aethermind-cli",
            "--store-kind",
            "remote-work",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    layer = payload["layer"]
    assert layer["next"] == ["verify the downstream adapter"]
    assert layer["remote_target"] == "example-host:/srv/app"
    assert layer["local_store_reason"] == "continuity remains local"
    assert layer["source_tool"] == "aethermind-cli"
    assert layer["store_kind"] == "remote-work"
