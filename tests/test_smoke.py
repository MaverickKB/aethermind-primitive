"""Basic behavior checks for the public Python API."""

from aethermind import AetherMind


def test_smoke(tmp_path):
    aether = AetherMind(tmp_path, create=True)

    written = aether.write_layer(
        type="load-bearing",
        body="!This is a test layer",
        ctx="test/smoke",
        conf=0.95,
        markers=["!"],
    )
    aether.write_texture(
        body="~This is a test texture entry",
        ctx="test/smoke",
        marker="~",
    )

    layers = aether.read_layers(ctx="test/smoke")
    assert len(layers) == 1
    layer = layers[0]
    assert layer.type == "load-bearing"
    assert layer.ctx == "test/smoke"
    assert layer.conf == 0.95
    assert layer.body == "!This is a test layer"
    assert layer.id == written.id

    texture = aether.read_texture()
    assert "[unknown | test/smoke]" in texture
    assert "~This is a test texture entry" in texture
    assert texture.endswith("---\n")
