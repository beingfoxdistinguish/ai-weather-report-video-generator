"""Dependency wiring: assemble adapters + services into a single pipeline."""

from __future__ import annotations

from weathercast.adapters.ffmpeg_adapter import FFmpegAdapter
from weathercast.adapters.forecast_adapter import ForecastAdapter
from weathercast.adapters.tts_adapter import TTSAdapter
from weathercast.config.settings import Settings
from weathercast.services.narration_service import NarrationService
from weathercast.services.render_service import RenderService
from weathercast.services.script_service import ScriptService


class WeatherReportPipeline:
    """Orchestrates: forecast -> script -> narration -> render."""

    def __init__(
        self,
        forecast: ForecastAdapter,
        script: ScriptService,
        narration: NarrationService,
        render: RenderService,
    ) -> None:
        self._forecast = forecast
        self._script = script
        self._narration = narration
        self._render = render

    async def self_check(self) -> int:
        ok = True
        ok &= await self._forecast.ping()
        ok &= self._narration.backend_available()
        ok &= self._render.ffmpeg_available()
        return 0 if ok else 1

    async def preview(self, location: str) -> None:
        report = await self._forecast.fetch(location)
        script = self._script.compose(report)
        await self._narration.synthesize(script)

    async def generate(self, location: str, out_dir: object) -> None:
        report = await self._forecast.fetch(location)
        script = self._script.compose(report)
        track = await self._narration.synthesize(script)
        await self._render.render(script, track, out_dir)


def build_pipeline(settings: Settings, provider_override: str | None = None) -> WeatherReportPipeline:
    forecast = ForecastAdapter(settings, provider_override)
    script = ScriptService(settings)
    narration = NarrationService(settings)
    render = RenderService(settings, FFmpegAdapter(settings), TTSAdapter(settings))
    return WeatherReportPipeline(forecast, script, narration, render)