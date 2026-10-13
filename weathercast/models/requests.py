"""Request schemas for handlers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class GenerateRequest:
    location: str
    out_dir: Path
    fps: int = 30
    provider: str | None = None


@dataclass(frozen=True, slots=True)
class PreviewRequest:
    location: str
    provider: str | None = None