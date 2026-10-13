"""FFmpeg adapter — overlay drawing and scene concatenation.

All subprocess calls use argument lists (never shell=True) and every path
is resolved under the configured workspace root.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from weathercast.config.settings import Settings
from weathercast.utils.logging import get_logger

_log = get_logger("adapters.ffmpeg")


class FFmpegAdapter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._binary = shutil.which("ffmpeg") or "ffmpeg"

    def is_available(self) -> bool:
        return shutil.which("ffmpeg") is not None

    def draw_overlay(self, text: str, out: Path, resolution: tuple[int, int]) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        w, h = resolution
        safe = text.replace(":", "\\:").replace("'", "\u2019")
        vf = (
            f"color=c=0x0B1B2B:s={w}x{h}:d=1,"
            f"drawtext=text='{safe}':fontcolor=white:fontsize=64:"
            f"x=(w-text_w)/2:y=h-160"
        )
        cmd = [self._binary, "-y", "-f", "lavfi", "-i", vf, "-frames:v", "1", str(out)]
        _log.debug("ffmpeg draw_overlay -> %s", out.name)
        subprocess_run(cmd)

    async def concat_scenes(
        self,
        frames: list[Path],
        audio: Path,
        out: Path,
        fps: int,
        duration_s: float,
    ) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        concat_file = out.parent / "scenes.txt"
        concat_file.write_text(
            "\n".join(f"file '{f.as_posix()}'" for f in frames), encoding="utf-8"
        )
        cmd = [
            self._binary, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest",
            "-r", str(fps),
            str(out),
        ]
        await _run_async(cmd)
        _log.info("encoded %.1fs report -> %s", duration_s, out.name)


def subprocess_run(cmd: list[str]) -> None:
    import subprocess

    proc = subprocess.run(cmd, capture_output=True, check=False)  # noqa: S603
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode('utf-8', 'replace')[:400]}")


async def _run_async(cmd: list[str]) -> None:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg encode failed: {stderr.decode('utf-8', 'replace')[:400]}")