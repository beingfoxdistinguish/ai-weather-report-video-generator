"""Turn a weather script into a narration audio track via a TTS adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from weathercast.adapters.tts_adapter import TTSAdapter
from weathercast.config.settings import Settings
from weathercast.services.script_service import WeatherScript
from weathercast.utils.logging import get_logger

_log = get_logger("services.narration")


@dataclass(frozen=True, slots=True)
class NarrationTrack:
    audio_path: Path
    duration_s: float
    cue_points: tuple[float, ...]


class NarrationService:
    def __init__(self, settings: Settings, adapter: TTSAdapter | None = None) -> None:
        self._settings = settings
        self._tts = adapter or TTSAdapter(settings)

    def backend_available(self) -> bool:
        return self._tts.is_available()

    async def synthesize(self, script: WeatherScript) -> NarrationTrack:
        out_dir = self._settings.workspace / "narration"
        out_dir.mkdir(parents=True, exist_ok=True)
        audio_path = out_dir / "voiceover.wav"

        cue_points: list[float] = []
        cursor = 0.0
        for seg in script.segments:
            cue_points.append(round(cursor, 3))
            cursor += seg.duration_s

        _log.info("synthesizing %d segments -> %s", len(script.segments), audio_path.name)
        await self._tts.synthesize_segments(
            [s.narration for s in script.segments], audio_path, self._settings.voice
        )
        return NarrationTrack(
            audio_path=audio_path,
            duration_s=round(cursor, 3),
            cue_points=tuple(cue_points),
        )