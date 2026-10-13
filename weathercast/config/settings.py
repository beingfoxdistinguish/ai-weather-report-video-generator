"""Typed settings loaded from YAML + environment overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_DEFAULTS: dict[str, object] = {
    "workspace": "renders",
    "resolution": [1920, 1080],
    "fps": 30,
    "voice": "en_US-amy-medium",
    "provider": "open-meteo",
    "template_pack": "broadcast_classic",
}


@dataclass(frozen=True, slots=True)
class Settings:
    workspace: Path
    resolution: tuple[int, int]
    fps: int
    voice: str
    provider: str
    template_pack: str
    api_keys: dict[str, str] = field(default_factory=dict)
    raw: dict[str, object] = field(default_factory=dict)


def load_settings(config_path: Path | None = None) -> Settings:
    data: dict[str, object] = dict(_DEFAULTS)
    if config_path and config_path.exists():
        data.update(yaml.safe_load(config_path.read_text(encoding="utf-8")) or {})

    res = data.get("resolution", [1920, 1080])
    if not (isinstance(res, (list, tuple)) and len(res) == 2):
        raise ValueError(f"resolution must be [w, h], got {res!r}")

    keys = {
        "OPEN_METEO_TOKEN": os.getenv("OPEN_METEO_TOKEN", ""),
        "WEATHERAPI_KEY": os.getenv("WEATHERAPI_KEY", ""),
    }

    return Settings(
        workspace=Path(str(data["workspace"])),
        resolution=(int(res[0]), int(res[1])),
        fps=int(data.get("fps", 30)),  # type: ignore[arg-type]
        voice=str(data["voice"]),
        provider=str(data["provider"]),
        template_pack=str(data["template_pack"]),
        api_keys={k: v for k, v in keys.items() if v},
        raw=data,
    )