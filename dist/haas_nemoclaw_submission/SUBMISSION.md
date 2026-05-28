# SUBMISSION

## One-Line Pitch

HaaS NemoClaw Long Agent is an offline-first Human-in-the-Loop marketplace-ops agent that turns public help signals into safe task drafts while persisting checkpoints, guardrail decisions, and audit logs.

## What Judges Should Run

Fastest unattended proof:

```bash
python3 main.py demo --auto-answer
```

Full persistence proof:

```bash
python3 main.py demo
python3 main.py status --run-id <RUN_ID>
python3 main.py answer --run-id <RUN_ID> --checkpoint-id <CHECKPOINT_ID> --decision approve-draft-only-invite --notes "Keep outreach draft-only."
python3 main.py run --run-id <RUN_ID>
python3 main.py report --run-id <RUN_ID>
```

Guardrail proof:

```bash
python3 main.py guardrail-demo
```

Browser demo:

```bash
python3 main.py ui --port 8765
```

## Why It Matters

Public social platforms contain many requests for human judgment, local knowledge, and subjective experience. HaaS needs an operations agent that can triage those signals into tasks without spamming people, exposing private data, giving personalized financial advice, or moving funds without approval.

This project makes those judgment gates explicit, durable, and auditable.

## Competition Alignment

- Real task execution: HaaS marketplace lead triage and task drafting.
- Long-running behavior: pause, persist, resume, complete.
- NemoClaw fit: policy layer blocks unsafe actions and rewrites risky autonomy into checkpoints.
- Nemotron fit: the same agent contract supports live NIM / Nemotron when networking is allowed.
- Deployable code: Python standard library only for the default path.

## Deliverables

- `main.py`
- `haas_nemoclaw/`
- `web_ui/`
- `tests/`
- `README.md`
- `SETUP.md`
- `DEMO.md`
- `ARCHITECTURE.md`
- `SAFETY.md`

## Live Model Usage

The default path is intentionally offline and deterministic. If judges allow networking:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```
