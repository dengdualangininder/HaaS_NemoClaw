# SETUP

## Goal

Open and run the repo in a restricted NemoClaw-style environment without installing third-party packages.

## Requirements

- Python 3.11+ recommended
- No npm
- No pip install required for the default demo path

## Project open sequence

1. Open the project root.
2. Confirm Python is available:

```bash
python3 --version
```

3. Run the offline demo:

```bash
python3 main.py demo
```

4. Or run the visual dashboard:

```bash
python3 main.py ui --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

Dashboard runtime modes:

- `Offline Demo`: no key required, no network required
- `NVIDIA NIM`: enter the API key in the browser, choose a model, click `Connect NIM`, then start a run

## Dependency model

The default path uses only Python standard library modules:

- `argparse`
- `dataclasses`
- `datetime`
- `json`
- `pathlib`
- `sqlite3`
- `urllib`
- `uuid`

No `requirements.txt` install step is needed.

## Runtime files

The app writes only project-owned runtime state:

- `runtime/haas_nemoclaw.db`

This database is created automatically on first run.

## Optional live Nemotron setup

Only do this if the environment is allowed to reach NVIDIA NIM:

```bash
python3 main.py ui --port 8765
```

Then in the browser:

1. Switch the inference panel to `NVIDIA NIM`
2. Paste `NVIDIA_API_KEY`
3. Keep `https://integrate.api.nvidia.com/v1` unless you use another endpoint
4. Select a model
5. Click `Connect NIM`
6. Start a run

CLI alternative:

```bash
export NVIDIA_API_KEY="<your-key>"
export NIM_BASE_URL="https://integrate.api.nvidia.com/v1"
python3 main.py demo --reasoner nim --nim-model nvidia/llama-3.3-nemotron-super-49b-v1
```

If the environment is restricted, stay on the default `scripted_nemotron` backend.

## What NemoClaw should open first

1. `README.md`
2. `DEMO.md`
3. `ARCHITECTURE.md`
4. `SAFETY.md`

## Troubleshooting

If you see “run not found”:

- Re-check the `run_id`
- Confirm the same project directory is being used
- Inspect current runs:

```bash
python3 main.py runs
```

If you see “NVIDIA_API_KEY is required”:

- You selected the live NIM backend without connecting credentials
- Either connect from the dashboard, set the environment variable, or switch back to the default offline backend
