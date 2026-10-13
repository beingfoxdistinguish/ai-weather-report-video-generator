"""Structured forecast domain models."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DailyForecast:
    date: dt.date
    weekday: str
    high_c: int
    low_c: int
    precip_prob: int
    summary: str


@dataclass(frozen=True, slots=True)
class WeatherReport:
    location: str
    valid_date: dt.date
    days: tuple[DailyForecast, ...]

    def hottest(self) -> DailyForecast:
        return max(self.days, key=lambda d: d.high_c)

    def wettest(self) -> DailyForecast:
        return max(self.days, key=lambda d: d.precip_prob)