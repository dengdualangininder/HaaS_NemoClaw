# HaaS / NemoClaw Handoff

This repo now hands off to a Python long-agent implementation rather than the older HTML-first demo path.

## Read in this order

1. [README.md](README.md)
2. [SETUP.md](SETUP.md)
3. [DEMO.md](DEMO.md)
4. [ARCHITECTURE.md](ARCHITECTURE.md)
5. [SAFETY.md](SAFETY.md)

## Primary entrypoint

```bash
python3 main.py demo
```

## What changed

The primary submission path is now:

- offline-first
- restartable
- backed by SQLite persistence
- driven by explicit policy guardrails
- suitable for restricted NemoClaw environments

The legacy HTML and JSX files remain in the repo only as presentation artifacts.
