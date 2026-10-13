"""Compose a broadcast-style weather script from a structured report.

The script is a list of timed segments; each segment maps to one scene in
the final video. Timing is derived from a words-per-minute model so the
narration track and the scene timeline stay in sync.
"""

from __future__ import annotations

from dataclasses import dataclass

from weathercast.config.settings import Settings
from weathercast.models.forecast import WeatherReport

# Average narration pace for the synthesizer voice, in words per minute.
_WPM = 155.0


@dataclass(frozen=True, slots=True)
class ScriptSegment:
    index: int
    narration: str
    overlay: str
    duration_s: float


@dataclass(frozen=True, slots=True)
class WeatherScript:
    location: str
    segments: tuple[ScriptSegment, ...]

    @property
    def total_duration_s(self) -> float:
        return sum(s.duration_s for s in self.segments)


class ScriptService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def compose(self, report: WeatherReport) -> WeatherScript:
        segments: list[ScriptSegment] = []
        intro = (
            f"Good evening. Here is your weather report for {report.location} "
            f"for {report.valid_date:%A, %B %d}."
        )
        segments.append(self._segment(0, intro, overlay=report.location))

        for i, day in enumerate(report.days, start=1):
            narration = (
                f"{day.weekday}: {day.summary}. High of {day.high_c} degrees, "
                f"low of {day.low_c}. {day.precip_prob} percent chance of precipitation."
            )
            overlay = f"{day.weekday}  H:{day.high_c}°  L:{day.low_c}°"
            segments.append(self._segment(i, narration, overlay))

        outro_index = len(segments)
        segments.append(
            self._segment(
                outro_index,
                f"That is your forecast for {report.location}. Stay safe out there.",
                overlay="Stay safe",
            )
        )
        return WeatherScript(location=report.location, segments=tuple(segments))

    @staticmethod
    def _segment(index: int, narration: str, overlay: str) -> ScriptSegment:
        words = len(narration.split())
        duration = max(1.5, (words / _WPM) * 60.0)
        return ScriptSegment(index=index, narration=narration, overlay=overlay, duration_s=round(duration, 2))