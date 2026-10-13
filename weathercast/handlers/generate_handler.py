"""Handler for a single generate request. No business logic lives here."""

from __future__ import annotations

from pathlib import Path

from weathercast.bootstrap.wiring import WeatherReportPipeline
from weathercast.models.requests import GenerateRequest
from weathercast.utils.logging import get_logger

_log = get_logger("handlers.generate")


async def handle_generate(
    pipeline: WeatherReportPipeline,
    request: GenerateRequest,
) -> Path:
    """Validate the request and delegate to the pipeline.

    Returns the render output directory. Raises ValueError on a malformed
    location string before any network call is made.
    """
    if not request.location.strip():
        raise ValueError("location must be non-empty")
    if request.fps <= 0 or request.fps > 120:
        raise ValueError(f"fps out of range: {request.fps}")

    _log.info("generate requested location=%r fps=%d", request.location, request.fps)
    await pipeline.generate(request.location, request.out_dir)
    return request.out_dir