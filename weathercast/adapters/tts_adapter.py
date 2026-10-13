"""TTS adapter — invokes a local Piper/piper-tts binary per segment.

*piper-tts >= 1.2 writes WAV headers differently than 1.1 — the concat
step below strips and rebuilds the header, so pin the version in CI.*
"""

from __future__ import annotations

import asyncio
import shutil
import wave
from pathlib import Path

from weathercast.config.settings import Settings
from weathercast.utils.logging import get_logger

_log = get_logger("adapters.tts")


class TTSAdapter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._binary = shutil.which("piper") or "piper"

    def is_available(self) -> bool:
        return shutil.which("piper") is not None

    async def synthesize_segments(
        self,
        segments: list[str],
        out: Path,
        voice: str,
    ) -> Path:
        out.parent.mkdir(parents=True, exist_ok=True)
        part_dir = out.parent / "parts"
        part_dir.mkdir(exist_ok=True)

        parts: list[Path] = []
        for i, text in enumerate(segments):
            part = part_dir / f"seg_{i:02d}.wav"
            cmd = [self._binary, "--model", voice, "--output_file", str(part)]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate(text.encode("utf-8"))
            if proc.returncode != 0:
                raise RuntimeError(f"piper failed on segment {i}: {stderr.decode('utf-8', 'replace')[:200]}")
            parts.append(part)

        _concat_wavs(parts, out)
        return out


def _concat_wavs(parts: list[Path], out: Path) -> None:
    """Concatenate WAV parts into a single track with a rebuilt header."""
    with wave.open(str(out), "wb") as dst:
        params_set = False
        for part in parts:
            with wave.open(str(part), "rb") as src:
                if not params_set:
                    dst.setparams(src.getparams())
                    params_set = True
                dst.writeframes(src.readframes(src.getnframes()))
    _log.info("concatenated %d TTS parts -> %s", len(parts), out.name)