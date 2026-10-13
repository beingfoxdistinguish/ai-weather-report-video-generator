# Contributing to ai-weather-report-video-generator

Thanks for wanting to help build the AI weather report video generator. This
project turns structured forecast data into a fully-rendered, narrated weather
broadcast video (voiceover, on-screen maps, lower-third graphics, and a
presenter avatar). Contributions of every size are welcome — new TTS backends,
render adapters, forecast providers, and template packs especially.

## Development setup

```bash
git clone https://github.com/community/ai-weather-report-video-generator
cd ai-weather-report-video-generator
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
python -m weathercast.bootstrap --check
```

The `--check` flag validates that FFmpeg, a TTS backend, and at least one
forecast provider are reachable before you start a full render.

## Repository layout

- `weathercast/bootstrap/` — entry points, CLI, dependency self-check.
- `weathercast/services/` — business logic (scriptwriting, narration, render orchestration).
- `weathercast/handlers/` — thin request handlers that delegate to services.
- `weathercast/adapters/` — platform/backend adapters (FFmpeg, TTS engines, forecast APIs).
- `weathercast/models/` — dataclasses and typed schemas shared across layers.
- `weathercast/config/` — settings loading, defaults, secrets resolution.
- `weathercast/utils/` — logging, timing, filesystem helpers.

## Coding standards

- Python 3.11+, type hints on every public function.
- `ruff` for lint, `mypy --strict` for types. Both run in CI.
- One pattern, one module. Keep adapters free of business logic.
- No business logic in handlers — they parse, validate, delegate, return.

## Pull requests

1. Branch from `main`: `git checkout -b feat/your-thing`.
2. Add or update tests under `tests/`.
3. Run `ruff check . && mypy weathercast && pytest`.
4. Open the PR with a short description of the render pipeline impact.

## Reporting rendering bugs

Attach the `render_id`, the source forecast JSON, and the generated `*.log`
from `renders/<render_id>/`. Without those three we can't reproduce timing
drift between the narration track and the scene timeline.