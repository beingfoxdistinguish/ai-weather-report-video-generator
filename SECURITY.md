# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | yes       |
| < 0.3   | no        |

## Reporting a vulnerability

Open a private security advisory on GitHub, or email
`security@weathercast-oss.invalid` (placeholder — replace with the real
maintainer address before publishing). Do not open a public issue for
anything that could be exploited.

Please include: affected version, a minimal reproducer (forecast JSON +
config that triggers it), and the impact you observed.

## Threat model

The generator runs locally on a Windows desktop and processes:

- Forecast JSON pulled from third-party weather APIs.
- Template packs (Jinja2 + JSON) that may be loaded from untrusted sources.
- TTS engine binaries invoked as subprocesses.

Relevant hardening already in place:

- Template packs are rendered with `jinja2.sandbox.SandboxedEnvironment`.
- All subprocess calls go through `adapters/ffmpeg_adapter.py` and
  `adapters/tts_adapter.py`, which use argument lists (never `shell=True`)
  and validate every path against the configured workspace root.
- API keys are read from the environment or Windows Credential Manager, never
  written into render artifacts.

Out of scope: vulnerabilities in third-party TTS binaries or FFmpeg itself —
report those upstream.

## Known limitations

Render output directories are written with the invoking user's permissions.
Do not point the workspace at a shared/networked location on a multi-user box.