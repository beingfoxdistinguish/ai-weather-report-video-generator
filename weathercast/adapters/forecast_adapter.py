"""Fetch structured forecast data from a configured provider.

Defaults to Open-Meteo (keyless). *Open-Meteo rate-limits at ~10 req/min
per IP for the free tier — batch your locations or you will see 429s.*
"""

from __future__ import annotations

import datetime as dt

import httpx

from weathercast.config.settings import Settings
from weathercast.models.forecast import DailyForecast, WeatherReport
from weathercast.utils.logging import get_logger

_log = get_logger("adapters.forecast")

_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class ForecastAdapter:
    def __init__(self, settings: Settings, provider_override: str | None = None) -> None:
        self._settings = settings
        self._provider = provider_override or settings.provider
        self._client = httpx.AsyncClient(timeout=15.0)

    async def ping(self) -> bool:
        try:
            resp = await self._client.get(_FORECAST_URL, params={"latitude": 0, "longitude": 0})
            return resp.status_code < 500
        except httpx.HTTPError as exc:
            _log.warning("forecast ping failed: %s", exc)
            return False

    async def _geocode(self, location: str) -> tuple[float, float, str]:
        resp = await self._client.get(_GEOCODE_URL, params={"name": location, "count": 1})
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if not results:
            raise ValueError(f"could not geocode location: {location!r}")
        top = results[0]
        return float(top["latitude"]), float(top["longitude"]), str(top["name"])

    async def fetch(self, location: str) -> WeatherReport:
        lat, lon, name = await self._geocode(location)
        resp = await self._client.get(
            _FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": 5,
                "timezone": "auto",
            },
        )
        resp.raise_for_status()
        payload = resp.json()["daily"]

        days: list[DailyForecast] = []
        for i, date_str in enumerate(payload["time"]):
            days.append(
                DailyForecast(
                    date=dt.date.fromisoformat(date_str),
                    weekday=dt.date.fromisoformat(date_str).strftime("%A"),
                    high_c=int(round(payload["temperature_2m_max"][i])),
                    low_c=int(round(payload["temperature_2m_min"][i])),
                    precip_prob=int(payload["precipitation_probability_max"][i] or 0),
                    summary="Mixed conditions",
                )
            )
        return WeatherReport(location=name, valid_date=dt.date.today(), days=tuple(days))