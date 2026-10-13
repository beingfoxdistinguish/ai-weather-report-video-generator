"""Tests for the script composition service."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from weathercast.config.settings import Settings
from weathercast.models.forecast import DailyForecast, WeatherReport
from weathercast.services.script_service import ScriptService


def _settings() -> Settings:
    return Settings(
        workspace=Path("renders"),
        resolution=(1920, 1080),
        fps=30,
        voice="en_US-amy-medium",
        provider="open-meteo",
        template_pack="broadcast_classic",
    )


def _report() -> WeatherReport:
    days = tuple(
        DailyForecast(
            date=dt.date(2026, 3, 10 + i),
            weekday=f"Day{i}",
            high_c=20 + i,
            low_c=10 + i,
            precip_prob=i * 5,
            summary="Clear",
        )
        for i in range(5)
    )
    return WeatherReport(location="Austin, TX", valid_date=dt.date(2026, 3, 10), days=days)


def test_compose_produces_intro_days_and_outro() -> None:
    script = ScriptService(_settings()).compose(_report())
    # 1 intro + 5 days + 1 outro
    assert len(script.segments) == 7
    assert script.segments[0].index == 0
    assert script.segments[-1].overlay == "Stay safe"


def test_every_segment_has_positive_duration() -> None:
    script = ScriptService(_settings()).compose(_report())
    assert all(s.duration_s >= 1.5 for s in script.segments)


def test_total_duration_is_sum_of_segments() -> None:
    script = ScriptService(_settings()).compose(_report())
    expected = round(sum(s.duration_s for s in script.segments), 3)
    assert script.total_duration_s == pytest.approx(expected, abs=1e-3)