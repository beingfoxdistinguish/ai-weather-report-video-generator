"""Handler for a preview (script + timing) request."""

from __future__ import annotations

from weathercast.bootstrap.wiring import WeatherReportPipeline
from weathercast.models.requests import PreviewRequest


async def handle_preview(
    pipeline: WeatherReportPipeline,
    request: PreviewRequest,
) -> None:
    if not request.location.strip():
        raise ValueError("location must be non-empty")
    await pipeline.preview(request.location)