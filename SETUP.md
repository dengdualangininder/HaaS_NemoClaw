# SETUP

## Requirements

Default demo path:

- Python 3.10+
- Python standard library only
- no `pip install`
- no external API key
- no internet access required

## Start

```bash
python3 main.py demo
```

## Visual Dashboard

```bash
python3 main.py ui --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

If OpenClaw runs inside a Docker sandbox and needs to reach a host dashboard, use:

```text
http://host.docker.internal:8765
```

or bind the dashboard to all interfaces:

```bash
python3 main.py ui --host 0.0.0.0 --port 8765
```

## Runtime State

Default SQLite database:

```text
runtime/haas_nemoclaw.db
```

Use a custom path:

```bash
python3 main.py --db runtime/demo.db demo
```

## Verify

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Optional Live NIM

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```
