"""Tests for the 2026-07-02 MCP server upgrade:
- read_layers filters: since_ts, last_n, ctx_prefix, markers_any
- brief()
- auto-init guard (create flag)
"""
from __future__ import annotations

import pytest

from aethermind.core import AetherMind, AutoInitBlocked


def _seed(aether: AetherMind, ctx: str, ts: str, markers=None, **kwargs):
    return aether.layer_store.append(
        author="filters-test",
        type=kwargs.pop("type", "discovery"),
        body=kwargs.pop("body", f"layer for {ctx} @ {ts}"),
        ctx=ctx,
        conf=1.0,
        markers=markers or [],
        ts=ts,
        **kwargs,
    )


# --- read_layers filters -----------------------------------------------

def test_ctx_prefix_matches_segments_not_substrings(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    _seed(aether, "book4/ch2/topic", "2026-07-01T00:00:00Z")
    _seed(aether, "book4/ch2", "2026-07-01T00:00:01Z")
    _seed(aether, "book4/ch2x/topic", "2026-07-01T00:00:02Z")  # sibling segment, must not match
    _seed(aether, "book4x/ch2/topic", "2026-07-01T00:00:03Z")  # sibling segment, must not match

    matched = aether.read_layers(ctx_prefix="book4/ch2")

    assert {layer.ctx for layer in matched} == {"book4/ch2/topic", "book4/ch2"}


def test_since_ts_is_exclusive(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    _seed(aether, "t/since", "2026-07-01T00:00:00Z")
    second = _seed(aether, "t/since", "2026-07-01T00:00:01Z")
    third = _seed(aether, "t/since", "2026-07-01T00:00:02Z")

    after = aether.read_layers(since_ts="2026-07-01T00:00:00Z")

    assert [layer.id for layer in after] == [second.id, third.id]


def test_last_n_returns_newest_first_without_disturbing_default_order(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    first = _seed(aether, "t/lastn", "2026-07-01T00:00:00Z")
    second = _seed(aether, "t/lastn", "2026-07-01T00:00:01Z")
    third = _seed(aether, "t/lastn", "2026-07-01T00:00:02Z")

    default_order = aether.read_layers(ctx="t/lastn")
    newest_two = aether.read_layers(ctx="t/lastn", last_n=2)

    assert [layer.id for layer in default_order] == [first.id, second.id, third.id]
    assert [layer.id for layer in newest_two] == [third.id, second.id]


def test_markers_any_matches_intersection(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    _seed(aether, "t/markers", "2026-07-01T00:00:00Z", markers=["RULE"])
    _seed(aether, "t/markers", "2026-07-01T00:00:01Z", markers=["RES"])
    _seed(aether, "t/markers", "2026-07-01T00:00:02Z", markers=[])

    matched = aether.read_layers(ctx="t/markers", markers_any=["RULE", "RES"])

    assert len(matched) == 2


def test_filters_are_composable_with_existing_filters(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    _seed(aether, "book4/ch3/topic", "2026-07-01T00:00:00Z", markers=["RULE"], type="correction")
    _seed(aether, "book4/ch3/topic", "2026-07-01T00:00:01Z", markers=["RULE"], type="discovery")
    _seed(aether, "book4/ch3/other", "2026-07-01T00:00:02Z", markers=["RULE"], type="correction")

    matched = aether.read_layers(
        ctx_prefix="book4/ch3",
        type="correction",
        markers_any=["RULE"],
    )

    assert len(matched) == 2
    assert all(layer.type == "correction" for layer in matched)


def test_old_read_layers_signature_and_order_unchanged(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    aether.write_layer(type="discovery", body="first", ctx="t/oldsig", conf=1.0, markers=[])
    aether.write_layer(type="discovery", body="second", ctx="t/oldsig", conf=1.0, markers=[])

    # positional ctx/type/author still work exactly as before
    readback = aether.read_layers("t/oldsig", None, None)
    assert [layer.body for layer in readback] == ["first", "second"]


# --- brief() -------------------------------------------------------------

def test_brief_returns_newest_digest_per_ctx_and_post_digest_deltas(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    _seed(aether, "book4/ch1/digest", "2026-07-01T00:00:00Z", type="load-bearing")
    ch1_digest_2 = _seed(aether, "book4/ch1/digest", "2026-07-01T00:00:05Z", type="load-bearing")
    ch2_digest = _seed(aether, "book4/ch2/digest", "2026-07-01T00:00:10Z", type="load-bearing")
    delta1 = _seed(aether, "book4/ch2/scene1", "2026-07-01T00:00:11Z")
    delta2 = _seed(aether, "book4/ch2/scene2", "2026-07-01T00:00:12Z")

    result = aether.brief()

    digest_ids = {layer.id for layer in result["digests"]}
    assert digest_ids == {ch1_digest_2.id, ch2_digest.id}  # newest per ctx only
    assert result["newest_digest_ts"] == ch2_digest.ts
    assert [layer.id for layer in result["deltas"]] == [delta1.id, delta2.id]
    assert result["layer_count"] == 5


def test_brief_with_no_digests_returns_full_store_as_deltas(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    aether.write_layer(type="discovery", body="no digest yet", ctx="book4/ch1/scene1", conf=1.0, markers=[])

    result = aether.brief()

    assert result["digests"] == []
    assert result["newest_digest_ts"] is None
    assert len(result["deltas"]) == 1


def test_brief_on_empty_store_is_empty_not_an_error(tmp_path):
    aether = AetherMind(tmp_path, create=True)
    result = aether.brief()
    assert result == {
        "digests": [],
        "deltas": [],
        "newest_digest_ts": None,
        "layer_count": 0,
        "type_breakdown": {},
    }


# --- auto-init guard -------------------------------------------------------

def test_write_without_create_on_new_root_is_blocked(tmp_path):
    fresh_root = tmp_path / "never-touched"
    aether = AetherMind(fresh_root, create=False)

    assert aether.layer_store is None
    assert not (fresh_root / ".aethermind").exists()

    with pytest.raises(AutoInitBlocked):
        aether.write_layer(type="discovery", body="blocked", ctx="t/guard", conf=1.0, markers=[])

    with pytest.raises(AutoInitBlocked):
        aether.write_texture(body="blocked", ctx="t/guard")

    # Blocked writes must never touch disk.
    assert not (fresh_root / ".aethermind").exists()


def test_reads_on_new_root_are_empty_not_errors(tmp_path):
    fresh_root = tmp_path / "never-touched-2"
    aether = AetherMind(fresh_root, create=False)

    assert aether.read_layers() == []
    assert aether.read_texture() == ""
    assert aether.status_summary()["layer_count"] == 0
    assert aether.brief()["layer_count"] == 0
    assert not (fresh_root / ".aethermind").exists()


def test_create_true_still_initializes_a_new_store(tmp_path):
    fresh_root = tmp_path / "explicit-create"
    aether = AetherMind(fresh_root, create=True)
    written = aether.write_layer(type="discovery", body="explicit create", ctx="t/guard", conf=1.0, markers=[])
    assert written.id == "0001"
    assert (fresh_root / ".aethermind").exists()


def test_default_create_is_safe_for_library_callers(tmp_path):
    fresh_root = tmp_path / "default-call"
    aether = AetherMind(fresh_root)
    with pytest.raises(AutoInitBlocked):
        aether.write_layer(
            type="discovery",
            body="default call",
            ctx="t/guard",
            conf=1.0,
            markers=[],
        )
    assert not (fresh_root / ".aethermind").exists()


def test_existing_store_is_always_writable_regardless_of_create_flag(tmp_path):
    root = tmp_path / "existing"
    bootstrap = AetherMind(root, create=True)
    bootstrap.write_layer(type="discovery", body="seed", ctx="t/guard", conf=1.0, markers=[])

    # Now re-open with create=False: the store already exists, so writes
    # must still succeed without needing the flag again.
    reopened = AetherMind(root, create=False)
    written = reopened.write_layer(type="discovery", body="second", ctx="t/guard", conf=1.0, markers=[])
    assert written.id == "0002"
