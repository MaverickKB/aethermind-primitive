from __future__ import annotations

from aethermind.core import AetherMind


def test_core_write_layer_accepts_explicit_author(tmp_path):
    aether = AetherMind(str(tmp_path), create=True)

    written = aether.write_layer(
        type="discovery",
        body="> caller identity is retained",
        ctx="test/author",
        conf=0.99,
        markers=[">"],
        author="adapter-test",
    )
    layers = aether.read_layers(ctx="test/author")

    assert written.author == "adapter-test"
    assert len(layers) == 1
    assert layers[0].author == "adapter-test"
    assert layers[0].body == "> caller identity is retained"
