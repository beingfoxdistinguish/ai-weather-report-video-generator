"""Orchestrate scene composition and final video encode."""

from __future__ import annotations

from pathlib import Path

from weathercast.adapters.ffmpeg_adapter import FFmpegAdapter
from weathercast.adapters.tts_adapter import TTSAdapter
from weathercast.config.settings import Settings
from weathercast.services.narration_service import NarrationTrack
from weathercast.services.script_service import WeatherScript
from weathercast.utils.logging import get_logger

_log = get_logger("services.render")


class RenderService:
    def __init__(self, settings: Settings, ffmpeg: FFmpegAdapter, tts: TTSAdapter) -> None:
        self._settings = settings
        self._ffmpeg = ffmpeg
        self._tts = tts

    def ffmpeg_available(self) -> bool:
        return self._ffmpeg.is_available()

    async def render(
        self,
        script: WeatherScript,
        track: NarrationTrack,
        out_dir: object,
    ) -> Path:
        target = Path(str(out_dir)) / script.location.replace(",", "").replace(" ", "_")
        target.mkdir(parents=True, exist_ok=True)

        scene_frames: list[Path] = []
        for seg in script.segments:
            frame = target / f"scene_{seg.index:02d}.png"
            self._ffmpeg.draw_overlay(
                text=seg.overlay,
                out=frame,
                resolution=self._settings.resolution,
            )
            scene_frames.append(frame)

        output = target / "weather_report.mp4"
        _log.info("encoding %d scenes -> %s", len(scene_frames), output.name)
        await self._ffmpeg.concat_scenes(
            frames=scene_frames,
            audio=track.audio_path,
            out=output,
            fps=self._settings.fps,
            duration_s=track.duration_s,
        )
        return output