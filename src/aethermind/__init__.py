"""Public AetherMind primitive API.

The root-first helpers preserve the 0.1 API. The current continuity engine is
available through :class:`AetherMind` and the classes re-exported here.
"""

from .compat import (
    export_store,
    import_layers,
    init_store,
    read_layers,
    remote_note,
    validate_store,
    write_layer,
)
from .core import (
    AetherLayer,
    AetherMind,
    AetherMindParseError,
    AutoInitBlocked,
    EventStore,
    LayerReadIssue,
    LayerReadReport,
    LayerStore,
    LockUnavailableError,
    TextureStore,
    derive_currentness,
    error_payload,
    initialize_store,
    runtime_capabilities,
)

__version__ = "0.2.0"

__all__ = [
    "AetherLayer",
    "AetherMind",
    "AetherMindParseError",
    "AutoInitBlocked",
    "EventStore",
    "LayerReadIssue",
    "LayerReadReport",
    "LayerStore",
    "LockUnavailableError",
    "TextureStore",
    "derive_currentness",
    "error_payload",
    "export_store",
    "import_layers",
    "init_store",
    "initialize_store",
    "read_layers",
    "remote_note",
    "runtime_capabilities",
    "validate_store",
    "write_layer",
]
