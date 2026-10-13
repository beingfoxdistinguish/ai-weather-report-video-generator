"""Command-line entry point for the weather report video generator.

Subcommands:
    generate   Render a weather report video from a forecast source.
    check      Validate that FFmpeg, a TTS backend, and a provider are ready.
    preview    Render just the script + narration timing, no video encode.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from weathercast.bootstrap.wiring import build_pipeline
from weathercast.config.settings import load_settings
from weathercast.utils.logging import get_logger

_log = get_logger("bootstrap.cli")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="weathercast", description=__doc__)
    parser.add_argument("--config", type=Path, default=None, help="Path to a YAML config.")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Render a report video.")
    gen.add_argument("--location", required=True, help="e.g. 'Austin, TX'")
    gen.add_argument("--provider", default=None, help="Override forecast provider.")
    gen.add_argument("--out", type=Path, default=Path("renders"))

    check = sub.add_parser("check", help="Self-check dependencies.")
    check.add_argument("--provider", default=None)

    prev = sub.add_parser("preview", help="Script + timing only, no encode.")
    prev.add_argument("--location", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = load_settings(args.config)

    try:
        pipeline = build_pipeline(settings, provider_override=getattr(args, "provider", None))
        if args.command == "check":
            return asyncio.run(pipeline.self_check())
        if args.command == "preview":
            asyncio.run(pipeline.preview(args.location))
            return 0
        asyncio.run(pipeline.generate(args.location, args.out))
        return 0
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error
        _log.error("pipeline failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())