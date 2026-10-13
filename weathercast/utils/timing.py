"""Timing helpers for keeping narration and scene timelines in sync."""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
from time import perf_counter
from weathercast.utils.logging import get_logger

_log = get_logger("utils.timing")


@contextmanager
def timed(label: str) -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    finally:
        _log.info("%s took %.3fs", label, perf_counter() - start)


def words_to_seconds(text: str, wpm: float) -> float:
    """Estimate spoken duration for a phrase at a given pace."""
    if wpm <= 0:
        raise ValueError("wpm must be positive")
    return (len(text.split()) / wpm) * 60.0