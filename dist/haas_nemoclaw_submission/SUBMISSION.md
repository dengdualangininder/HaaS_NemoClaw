# SUBMISSION

## One-line pitch

HaaS NemoClaw Long Agent is an offline-first Human-in-the-Loop contract review agent that persists state across interruptions and uses policy guardrails to force human approval on risky decisions.

## What judges should run

### Fastest unattended proof

```bash
python3 main.py demo --auto-answer
```

### Full persistence proof

```bash
python3 main.py demo
python3 main.py status --run-id <RUN_ID>
python3 main.py answer --run-id <RUN_ID> --checkpoint-id <CHECKPOINT_ID> --decision request-liability-cap --notes "Cap total liability at 12 months of fees."
python3 main.py run --run-id <RUN_ID>
python3 main.py report --run-id <RUN_ID>
```

### Guardrail proof

```bash
python3 main.py guardrail-demo
```

## Why it matters

Many agent demos either:

- do only shallow automation, or
- pretend to be autonomous while hiding the moments where human judgment is actually required.

This project makes those judgment gates explicit and durable.

## Competition alignment

- Real task execution: contract risk triage and negotiation planning
- Long-running behavior: pause, persist, resume, complete
- NemoClaw fit: policy layer blocks unsafe actions and rewrites risky autonomy into checkpoints
- Nemotron fit: same agent contract supports a live NIM backend when network is allowed
- Deployable code: Python standard library only for the default path

## Deliverables in this repo

- `README.md`
- `SETUP.md`
- `DEMO.md`
- `ARCHITECTURE.md`
- `SAFETY.md`
- `main.py`
- `haas_nemoclaw/`
- `tests/`
- `scripts/verify_submission.sh`
- `scripts/package_submission.sh`

## Notes on live model usage

The default submission path is intentionally offline and deterministic for restricted environments.

If judges want the live model path and have allowed networking, the same CLI supports:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/llama-3.3-nemotron-super-49b-v1
```
