# HaaS NemoClaw Long Agent

HaaS NemoClaw Long Agent is an offline-first marketplace-operations agent tailored for restricted NemoClaw / OpenClaw environments.

It solves one concrete workflow:

> Turn public help signals into safe HaaS task drafts, pause before external outreach or payout-sensitive actions, persist state durably, resume after interruption, and produce an auditable ops report without arbitrary web browsing or host-file access.

## Why This Problem

HaaS is a human task marketplace. The hard operational problem is not simply generating task text; it is safely turning messy public signals into actionable tasks while preserving review gates.

The agent can:

- Review bundled public help signals.
- Draft low-risk HaaS quests.
- Reject doxxing, stalking, confrontation, or private-data requests.
- Rewrite personalized financial advice into general educational risk discussion.
- Pause for human approval before external outreach or reward-sensitive actions.
- Persist runs, checkpoints, audit events, and final reports in SQLite.

## Competition Fit

- **Real problem-solving:** HaaS marketplace lead triage and task operations.
- **Long-running autonomy:** plan, analyze, pause, resume, complete.
- **Persistence:** SQLite-backed runs, checkpoints, events, and reports.
- **Stability:** deterministic offline demo path with Python standard library only.
- **Guardrails:** policy layer rejects unsafe actions and rewrites risky autonomy into checkpoints.
- **Deployability:** `python3 main.py ...` works without package installation.

## NemoClaw-First Design

The default runtime assumes a constrained environment:

- No arbitrary internet access.
- No arbitrary host filesystem reads.
- No package installation.
- Only project-owned runtime state is written locally.

Instead of reaching outside the sandbox, the agent uses:

- Bundled HaaS public-signal scenarios.
- Bundled operator policy defaults.
- SQLite state owned by this app.
- A reasoner adapter abstraction.

## Nemotron / NIM Integration Model

Two reasoner backends are supported:

1. `scripted_nemotron`
   - Default for restricted NemoClaw demos.
   - Fully offline and deterministic.
   - Emits the same planning, lead-analysis, checkpoint, and report contract as the live backend.

2. `nim`
   - Optional live backend for environments that can reach NVIDIA NIM.
   - Uses an OpenAI-compatible `POST /v1/chat/completions` endpoint.
   - Reads credentials from environment variables or the dashboard connection form.

The offline demo does not pretend to call live Nemotron. It demonstrates the same state-machine and guardrail contract with deterministic outputs so judges can replay it inside restricted sandboxes.

## Core Flow

```text
public signal queue
  -> plan HaaS ops review
  -> analyze leads one by one
  -> guardrail intercepts outreach / payout / finance / privacy risk
  -> create human checkpoint when approval is required
  -> persist run + audit log
  -> resume after answer
  -> synthesize final HaaS ops report
```

## Repository Guide

- `main.py`: CLI entrypoint.
- `main.py ui`: local visual dashboard entrypoint.
- `haas_nemoclaw/engine.py`: long-agent state machine.
- `haas_nemoclaw/dashboard.py`: local HTTP dashboard and runtime API.
- `haas_nemoclaw/guardrails.py`: policy-based guardrails.
- `haas_nemoclaw/reasoners.py`: offline and NIM-backed reasoners.
- `haas_nemoclaw/store.py`: SQLite persistence.
- `haas_nemoclaw/scenarios.py`: bundled HaaS ops scenarios.
- `SETUP.md`: setup for NemoClaw.
- `DEMO.md`: exact demo commands.
- `ARCHITECTURE.md`: runtime design.
- `SAFETY.md`: implemented guardrails and failure modes.
- `SUBMISSION.md`: judge-facing one-pager.

## Quick Start

Restricted-environment demo:

```bash
python3 main.py demo
```

Visual dashboard:

```bash
python3 main.py ui --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

Unattended proof:

```bash
python3 main.py demo --auto-answer
```

Guardrail proof:

```bash
python3 main.py guardrail-demo
```

## Example Operator Flow

1. Start a run:

```bash
python3 main.py demo
```

2. Inspect paused state:

```bash
python3 main.py status --run-id <RUN_ID>
```

3. Answer the checkpoint:

```bash
python3 main.py answer \
  --run-id <RUN_ID> \
  --checkpoint-id <CHECKPOINT_ID> \
  --decision approve-draft-only-invite \
  --notes "Keep outreach as a draft until HaaS Ops approves the connector path."
```

4. Resume:

```bash
python3 main.py run --run-id <RUN_ID>
```

5. Print report:

```bash
python3 main.py report --run-id <RUN_ID>
```

## Live NIM Usage

If networking is allowed:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```

The dashboard also supports switching to `NVIDIA NIM`, entering an API key, selecting a Nemotron model, and starting a live run. The key is kept in process memory and is not written to SQLite.

## Verification

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Legacy Assets

Historical HTML/JSX demos are preserved under `legacy/`. They are background material; the primary NemoClaw submission path is the SQLite-backed Long Agent runtime and dashboard.
