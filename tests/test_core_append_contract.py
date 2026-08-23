from __future__ import annotations

import pytest

from aethermind.core import AetherLayer, AetherMind, AetherMindParseError, LayerStore


def test_core_escapes_strings_as_valid_toml(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    body = 'quotes " backslash \\ newline\nkept'
    ctx = 'ctx/"quoted"'
    markers = ['>', '"']

    written = aether.write_layer(
        type="discovery",
        body=body,
        ctx=ctx,
        conf=0.8,
        markers=markers,
        author="escape-test",
    )
    readback = aether.read_layers(ctx=ctx)

    assert len(readback) == 1
    assert readback[0].id == written.id
    assert readback[0].body == body
    assert readback[0].ctx == ctx
    assert readback[0].markers == markers


def test_layer_store_rejects_duplicate_explicit_ids(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    store = LayerStore(path)
    layer = AetherLayer(
        id="0001",
        ts="2026-05-20T00:00:00Z",
        author="duplicate-test",
        type="discovery",
        body="first",
        ctx="append/contract",
        conf=1.0,
        markers=[],
    )

    store.write(layer)

    with pytest.raises(ValueError, match="duplicate layer id"):
        store.write(layer)


def test_core_allocates_ids_across_nonnumeric_history(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    store = LayerStore(path)
    store.write(AetherLayer(
        id="20260520-manual",
        ts="2026-05-20T00:00:00Z",
        author="manual",
        type="correction",
        body="manual layer",
        ctx="append/contract",
        conf=1.0,
        markers=[],
    ))

    first = store.append(
        author="test",
        type="discovery",
        body="first numeric",
        ctx="append/contract",
        conf=1.0,
        markers=[],
        ts="2026-05-20T00:00:01Z",
    )
    second = store.append(
        author="test",
        type="discovery",
        body="second numeric",
        ctx="append/contract",
        conf=1.0,
        markers=[],
        ts="2026-05-20T00:00:02Z",
    )

    assert first.id == "0001"
    assert second.id == "0002"


def test_layer_primitive_defaults_for_legacy_records(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    path.parent.mkdir()
    path.write_text(
        "[[layer]]\n"
        "id = \"0001\"\n"
        "ts = \"2026-05-23T00:00:00Z\"\n"
        "author = \"legacy\"\n"
        "type = \"discovery\"\n"
        "body = \"legacy layer without primitive\"\n"
        "ctx = \"light/layer\"\n"
        "conf = 1.0\n"
        "markers = []\n",
        encoding="utf-8",
    )

    layers = LayerStore(path).read()

    assert len(layers) == 1
    assert layers[0].primitive == "layer"


def test_layer_primitive_round_trips_for_new_writes(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="discovery",
        body="layer primitive readback",
        ctx="light/layer",
        conf=1.0,
        markers=[],
        author="primitive-test",
    )
    readback = aether.read_layers(ctx="light/layer")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert written.primitive == "layer"
    assert len(readback) == 1
    assert readback[0].primitive == "layer"
    assert 'primitive = "layer"' in text


def test_supersedes_relation_round_trips_on_newer_layer(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    original = aether.write_layer(
        type="discovery",
        body="original claim",
        ctx="light/supersession",
        conf=0.8,
        markers=[],
        author="relation-test",
    )
    replacement = aether.write_layer(
        type="correction",
        body="newer claim narrows the original",
        ctx="light/supersession",
        conf=0.9,
        markers=[],
        author="relation-test",
        supersedes=[original.id],
    )

    readback = aether.read_layers(ctx="light/supersession")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert [layer.id for layer in readback] == [original.id, replacement.id]
    assert readback[0].supersedes == []
    assert readback[1].supersedes == [original.id]
    assert f'supersedes = ["{original.id}"]' in text


def test_supersedes_relation_reads_existing_records(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    path.parent.mkdir()
    path.write_text(
        "[[layer]]\n"
        "id = \"0001\"\n"
        "ts = \"2026-05-23T00:00:00Z\"\n"
        "author = \"relation-test\"\n"
        "type = \"correction\"\n"
        "body = \"newer claim\"\n"
        "ctx = \"light/supersession\"\n"
        "conf = 0.9\n"
        "markers = []\n"
        "primitive = \"layer\"\n"
        "supersedes = [\"0000\"]\n",
        encoding="utf-8",
    )

    layers = LayerStore(path).read()

    assert len(layers) == 1
    assert layers[0].supersedes == ["0000"]


def test_supersedes_relation_rejects_scalar_toml_value(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    path.parent.mkdir()
    path.write_text(
        "[[layer]]\n"
        "id = \"0001\"\n"
        "ts = \"2026-05-23T00:00:00Z\"\n"
        "author = \"relation-test\"\n"
        "type = \"correction\"\n"
        "body = \"bad relation shape\"\n"
        "ctx = \"light/supersession\"\n"
        "conf = 0.9\n"
        "markers = []\n"
        "primitive = \"layer\"\n"
        "supersedes = \"0000\"\n",
        encoding="utf-8",
    )

    with pytest.raises(AetherMindParseError, match="supersedes must be an array"):
        LayerStore(path).read()


def test_rollback_of_relation_round_trips_on_newer_layer(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    original = aether.write_layer(
        type="discovery",
        body="claim later rolled back",
        ctx="light/rollback",
        conf=0.8,
        markers=[],
        author="rollback-test",
    )
    rollback = aether.write_layer(
        type="correction",
        body="rollback keeps the scar but removes current force",
        ctx="light/rollback",
        conf=0.95,
        markers=[],
        author="rollback-test",
        rollback_of=[original.id],
    )

    readback = aether.read_layers(ctx="light/rollback")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert [layer.id for layer in readback] == [original.id, rollback.id]
    assert readback[0].rollback_of == []
    assert readback[1].rollback_of == [original.id]
    assert f'rollback_of = ["{original.id}"]' in text


def test_rollback_of_relation_reads_existing_records(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    path.parent.mkdir()
    path.write_text(
        "[[layer]]\n"
        "id = \"0001\"\n"
        "ts = \"2026-05-23T00:00:00Z\"\n"
        "author = \"rollback-test\"\n"
        "type = \"correction\"\n"
        "body = \"rollback claim\"\n"
        "ctx = \"light/rollback\"\n"
        "conf = 0.95\n"
        "markers = []\n"
        "primitive = \"layer\"\n"
        "rollback_of = [\"0000\"]\n",
        encoding="utf-8",
    )

    layers = LayerStore(path).read()

    assert len(layers) == 1
    assert layers[0].rollback_of == ["0000"]


def test_rollback_of_relation_rejects_scalar_toml_value(tmp_path):
    path = tmp_path / ".aethermind" / "layers.aem"
    path.parent.mkdir()
    path.write_text(
        "[[layer]]\n"
        "id = \"0001\"\n"
        "ts = \"2026-05-23T00:00:00Z\"\n"
        "author = \"rollback-test\"\n"
        "type = \"correction\"\n"
        "body = \"bad rollback relation shape\"\n"
        "ctx = \"light/rollback\"\n"
        "conf = 0.95\n"
        "markers = []\n"
        "primitive = \"layer\"\n"
        "rollback_of = \"0000\"\n",
        encoding="utf-8",
    )

    with pytest.raises(AetherMindParseError, match="rollback_of must be an array"):
        LayerStore(path).read()


def test_artifact_reference_primitive_round_trips(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="discovery",
        body="core artifact reference",
        ctx="light/artifact-reference",
        conf=0.9,
        markers=[],
        author="artifact-test",
        primitive="artifact-reference",
        ref="lib/aethermind/core.py",
        kind="file",
        label="core writer",
    )

    readback = aether.read_layers(ctx="light/artifact-reference")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert written.primitive == "artifact-reference"
    assert len(readback) == 1
    assert readback[0].primitive == "artifact-reference"
    assert readback[0].ref == "lib/aethermind/core.py"
    assert readback[0].kind == "file"
    assert readback[0].label == "core writer"
    assert 'primitive = "artifact-reference"' in text
    assert 'ref = "lib/aethermind/core.py"' in text


def test_artifact_reference_primitive_requires_ref(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    with pytest.raises(ValueError, match="ref is required for artifact-reference primitive"):
        aether.write_layer(
            type="discovery",
            body="missing ref",
            ctx="light/artifact-reference",
            conf=0.9,
            markers=[],
            author="artifact-test",
            primitive="artifact-reference",
        )


def test_anchor_primitive_round_trips(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="discovery",
        body="anchor for core writer",
        ctx="light/anchor",
        conf=0.9,
        markers=[],
        author="anchor-test",
        primitive="anchor",
        artifact="lib/aethermind/core.py",
        anchor="aem-4f2c91ab",
        selector="AetherLayer",
        span_hint="dataclass fields",
        inline=True,
    )

    readback = aether.read_layers(ctx="light/anchor")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert written.primitive == "anchor"
    assert len(readback) == 1
    assert readback[0].artifact == "lib/aethermind/core.py"
    assert readback[0].anchor == "aem-4f2c91ab"
    assert readback[0].selector == "AetherLayer"
    assert readback[0].span_hint == "dataclass fields"
    assert readback[0].inline is True
    assert 'primitive = "anchor"' in text
    assert 'anchor = "aem-4f2c91ab"' in text
    assert "inline = true" in text


def test_anchor_primitive_requires_artifact_and_anchor(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    with pytest.raises(ValueError, match="anchor is required for anchor primitive"):
        aether.write_layer(
            type="discovery",
            body="missing anchor",
            ctx="light/anchor",
            conf=0.9,
            markers=[],
            author="anchor-test",
            primitive="anchor",
            artifact="lib/aethermind/core.py",
        )

    with pytest.raises(ValueError, match="artifact or artifact_ref is required for anchor primitive"):
        aether.write_layer(
            type="discovery",
            body="missing artifact",
            ctx="light/anchor",
            conf=0.9,
            markers=[],
            author="anchor-test",
            primitive="anchor",
            anchor="aem-4f2c91ab",
        )


def test_pressure_event_primitive_round_trips(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="friction",
        body="A worker selected the fallback runtime during critical work",
        ctx="light/pressure-event",
        conf=0.85,
        markers=["!"],
        author="pressure-test",
        primitive="pressure-event",
        domain="operations/worker-profile",
        symptom="worker selected the wrong runtime",
        evidence=["reports/continuity-check.md", "agent profile show"],
        next_verification="run primary-runtime smoke",
        suspected_mechanism="profile configuration incomplete",
        scope="profile",
        severity="high",
        recurrence_of=["pressure-0001"],
        owner_hint="worker profile config",
        repair="linked the shared runtime configuration",
    )

    readback = aether.read_layers(ctx="light/pressure-event")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert written.primitive == "pressure-event"
    assert len(readback) == 1
    assert readback[0].domain == "operations/worker-profile"
    assert readback[0].symptom == "worker selected the wrong runtime"
    assert readback[0].evidence == [
        "reports/continuity-check.md",
        "agent profile show",
    ]
    assert readback[0].next_verification == "run primary-runtime smoke"
    assert readback[0].suspected_mechanism == "profile configuration incomplete"
    assert readback[0].scope == "profile"
    assert readback[0].severity == "high"
    assert readback[0].recurrence_of == ["pressure-0001"]
    assert readback[0].owner_hint == "worker profile config"
    assert readback[0].repair == "linked the shared runtime configuration"
    assert 'primitive = "pressure-event"' in text
    assert 'domain = "operations/worker-profile"' in text
    assert (
        'evidence = ["reports/continuity-check.md", "agent profile show"]'
        in text
    )


def test_pressure_event_primitive_requires_pressure_fields(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    with pytest.raises(ValueError, match="domain is required for pressure-event primitive"):
        aether.write_layer(
            type="friction",
            body="missing domain",
            ctx="light/pressure-event",
            conf=0.85,
            markers=[],
            author="pressure-test",
            primitive="pressure-event",
            symptom="fallback",
            evidence=["log"],
            next_verification="smoke",
        )

    with pytest.raises(ValueError, match="symptom is required for pressure-event primitive"):
        aether.write_layer(
            type="friction",
            body="missing symptom",
            ctx="light/pressure-event",
            conf=0.85,
            markers=[],
            author="pressure-test",
            primitive="pressure-event",
            domain="operations/worker-profile",
            evidence=["log"],
            next_verification="smoke",
        )

    with pytest.raises(ValueError, match="evidence is required for pressure-event primitive"):
        aether.write_layer(
            type="friction",
            body="missing evidence",
            ctx="light/pressure-event",
            conf=0.85,
            markers=[],
            author="pressure-test",
            primitive="pressure-event",
            domain="operations/worker-profile",
            symptom="fallback",
            next_verification="smoke",
        )

    with pytest.raises(ValueError, match="next_verification is required for pressure-event primitive"):
        aether.write_layer(
            type="friction",
            body="missing next verification",
            ctx="light/pressure-event",
            conf=0.85,
            markers=[],
            author="pressure-test",
            primitive="pressure-event",
            domain="operations/worker-profile",
            symptom="fallback",
            evidence=["log"],
        )


def test_pressure_event_primitive_requires_friction_type(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    with pytest.raises(ValueError, match="pressure-event primitive requires type friction"):
        aether.write_layer(
            type="discovery",
            body="wrong type",
            ctx="light/pressure-event",
            conf=0.85,
            markers=[],
            author="pressure-test",
            primitive="pressure-event",
            domain="operations/worker-profile",
            symptom="fallback",
            evidence=["log"],
            next_verification="smoke",
        )


def test_supersession_primitive_round_trips(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="correction",
        body="standalone supersession claim",
        ctx="light/supersession-primitive",
        conf=0.95,
        markers=[],
        author="supersession-test",
        primitive="supersession",
        supersedes=["0001"],
        reason="newer claim narrows the old one",
        scope="claim",
        replacement="0002",
        artifact="lib/aethermind/core.py",
        anchor="aem-4f2c91ab",
    )

    readback = aether.read_layers(ctx="light/supersession-primitive")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert written.primitive == "supersession"
    assert len(readback) == 1
    assert readback[0].supersedes == ["0001"]
    assert readback[0].reason == "newer claim narrows the old one"
    assert readback[0].scope == "claim"
    assert readback[0].replacement == "0002"
    assert readback[0].artifact == "lib/aethermind/core.py"
    assert readback[0].anchor == "aem-4f2c91ab"
    assert 'primitive = "supersession"' in text
    assert 'supersedes = ["0001"]' in text
    assert 'reason = "newer claim narrows the old one"' in text


def test_supersession_primitive_requires_supersedes_and_reason(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    with pytest.raises(ValueError, match="supersedes is required for supersession primitive"):
        aether.write_layer(
            type="correction",
            body="missing supersedes",
            ctx="light/supersession-primitive",
            conf=0.95,
            markers=[],
            author="supersession-test",
            primitive="supersession",
            reason="newer claim narrows the old one",
        )

    with pytest.raises(ValueError, match="reason is required for supersession primitive"):
        aether.write_layer(
            type="correction",
            body="missing reason",
            ctx="light/supersession-primitive",
            conf=0.95,
            markers=[],
            author="supersession-test",
            primitive="supersession",
            supersedes=["0001"],
        )


def test_rollback_primitive_round_trips(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="correction",
        body="standalone rollback claim",
        ctx="light/rollback-primitive",
        conf=0.95,
        markers=[],
        author="rollback-test",
        primitive="rollback",
        rollback_of=["0001", "commit:abc123"],
        reason="the replacement introduced a regression",
        artifact="lib/aethermind/core.py",
        anchor="aem-4f2c91ab",
        restored_to="commit:def456",
        verification=["pytest lib/tests/test_core_append_contract.py -q"],
    )

    readback = aether.read_layers(ctx="light/rollback-primitive")
    text = (tmp_path / ".aethermind" / "layers.aem").read_text(encoding="utf-8")

    assert written.primitive == "rollback"
    assert len(readback) == 1
    assert readback[0].rollback_of == ["0001", "commit:abc123"]
    assert readback[0].reason == "the replacement introduced a regression"
    assert readback[0].artifact == "lib/aethermind/core.py"
    assert readback[0].anchor == "aem-4f2c91ab"
    assert readback[0].restored_to == "commit:def456"
    assert readback[0].verification == ["pytest lib/tests/test_core_append_contract.py -q"]
    assert 'primitive = "rollback"' in text
    assert 'rollback_of = ["0001", "commit:abc123"]' in text
    assert 'reason = "the replacement introduced a regression"' in text


def test_rollback_primitive_requires_rollback_of_and_reason(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    with pytest.raises(ValueError, match="rollback_of is required for rollback primitive"):
        aether.write_layer(
            type="correction",
            body="missing rollback_of",
            ctx="light/rollback-primitive",
            conf=0.95,
            markers=[],
            author="rollback-test",
            primitive="rollback",
            reason="the replacement introduced a regression",
        )

    with pytest.raises(ValueError, match="reason is required for rollback primitive"):
        aether.write_layer(
            type="correction",
            body="missing reason",
            ctx="light/rollback-primitive",
            conf=0.95,
            markers=[],
            author="rollback-test",
            primitive="rollback",
            rollback_of=["0001"],
        )
