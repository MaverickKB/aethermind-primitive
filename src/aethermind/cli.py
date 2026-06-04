from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .core import export_store, import_layers, init_store, read_layers, remote_note, validate_store, write_layer


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aethermind")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--author", default="aethermind-cli")
        p.add_argument("--json", action="store_true")

    p = sub.add_parser("init", help="initialize a local AetherMind store and write an init layer")
    p.add_argument("--root", required=True)
    p.add_argument("--purpose", required=True)
    add_common(p)

    p = sub.add_parser("layer", help="write a work layer")
    p.add_argument("--root", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--ctx", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--marker", action="append", dest="markers")
    p.add_argument("--evidence", action="append")
    add_common(p)

    p = sub.add_parser("remote-note", help="write local continuity for remote/customer work")
    p.add_argument("--remote", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--ctx", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--notes-root")
    p.add_argument("--evidence", action="append")
    add_common(p)

    p = sub.add_parser("validate", help="validate an AetherMind store")
    p.add_argument("--root", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("status", help="show AetherMind store status")
    p.add_argument("--root", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("inspect", help="print AetherMind layers for diagnostics")
    p.add_argument("--root", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("export", help="export AetherMind layers to a file")
    p.add_argument("--root", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("import", help="import AetherMind layers from a file")
    p.add_argument("--root", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            payload = init_store(args.root, purpose=args.purpose, author=args.author)
            _emit(payload, args.json)
        elif args.command == "layer":
            payload = write_layer(
                args.root,
                type=args.type,
                ctx=args.ctx,
                body=args.body,
                author=args.author,
                markers=args.markers,
                evidence=args.evidence,
            )
            _emit(payload, args.json)
        elif args.command == "remote-note":
            payload = remote_note(
                remote_target=args.remote,
                task=args.task,
                ctx=args.ctx,
                body=args.body,
                notes_root=args.notes_root,
                author=args.author,
                evidence=args.evidence,
            )
            _emit(payload, args.json)
        elif args.command in {"validate", "status"}:
            payload = validate_store(args.root)
            _emit(payload, args.json)
            return 0 if payload["ok"] else 1
        elif args.command == "inspect":
            payload = {"ok": True, "layers": read_layers(args.root)}
            _emit(payload, args.json)
        elif args.command == "export":
            payload = export_store(args.root, args.file)
            _emit(payload, args.json)
        elif args.command == "import":
            payload = import_layers(args.root, args.file)
            _emit(payload, args.json)
        return 0
    except Exception as exc:  # pragma: no cover - exercised by CLI users
        payload = {"ok": False, "error": str(exc)}
        _emit(payload, getattr(args, "json", False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
