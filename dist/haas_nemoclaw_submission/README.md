# HaaS NemoClaw Long Agent

HaaS NemoClaw Long Agent is a restartable, offline-first Human-in-the-Loop agent demo tailored for restricted NemoClaw environments.

It rewrites the repo around one concrete problem:

> Review a risky SaaS vendor agreement, pause whenever business judgment is required, persist state durably, resume after interruption, and produce a negotiation report without requiring arbitrary host file access or general internet browsing.

## Why this problem

This demo solves a specific and measurable workflow problem for SMB operators and consultants:

- A contract review contains both automatable work and judgment calls.
- The agent can classify clauses, flag known risk patterns, and prepare draft recommendations.
- The agent must not silently make subjective or high-risk decisions on behalf of the operator.
- The workflow must survive interruption because real approvals arrive asynchronously.

Measurable outputs in each run:

- Total clauses reviewed
- High-risk clauses flagged
- Human checkpoints created
- Guardrail interventions triggered
- Final negotiation actions produced

## Competition fit

This repo is intentionally optimized for the NVIDIA / NemoClaw judging criteria:

- Real problem-solving: contract risk triage and negotiation planning
- Long-running autonomy: the agent plans, analyzes, pauses, resumes, and completes
- Persistence: run state, checkpoints, and audit events are stored in SQLite
- Stability: deterministic offline demo path with zero external dependencies
- Guardrails: policy-based controls force human approval on risky decisions
- Deployability: `python main.py ...` with Python standard library only

## NemoClaw-first design

The runtime assumes a constrained environment:

- No arbitrary web access during the demo path
- No arbitrary host filesystem reads
- No package installation requirement
- Only project-owned runtime state is written locally

Instead of reaching outside the sandbox, the agent uses:

- Bundled scenario data
- Bundled operator policy defaults
- SQLite state owned by this app
- A reasoner adapter abstraction

## Nemotron integration model

There are two supported reasoner backends:

1. `scripted_nemotron`
   - Default for NemoClaw-restricted demos
   - Fully offline
   - Deterministic outputs shaped to the same decision contract as the live Nemotron backend

2. `nim`
   - Optional live backend for environments that can reach NVIDIA NIM or another OpenAI-compatible endpoint
   - Uses `POST /v1/chat/completions`
   - Reads credentials from environment variables only

The offline demo does not pretend to call live Nemotron. It demonstrates the same planner/checkpoint/report contract with a deterministic backend so the flow remains repeatable inside restricted sandboxes.

## Core flow

```text
scenario input
  -> plan the review
  -> analyze clauses one by one
  -> guardrail intercepts risky auto-decisions
  -> create human checkpoint
  -> persist run + audit log
  -> resume after answer
  -> synthesize final negotiation report
```

## Architecture at a glance

```text
CLI (main.py)
  -> LongAgentEngine
      -> Reasoner
         - scripted_nemotron
         - nim
      -> GuardrailPolicy
      -> SQLiteStore
          - runs
          - checkpoints
          - audit events
```

## Repository guide

- `main.py`: CLI entrypoint
- `main.py ui`: local visual dashboard entrypoint
- `haas_nemoclaw/engine.py`: long-agent state machine
- `haas_nemoclaw/dashboard.py`: local HTTP dashboard and runtime API
- `haas_nemoclaw/guardrails.py`: policy-based guardrails
- `haas_nemoclaw/reasoners.py`: offline and NIM-backed reasoners
- `haas_nemoclaw/store.py`: SQLite persistence
- `haas_nemoclaw/scenarios.py`: bundled demo scenarios
- `SETUP.md`: project setup for NemoClaw
- `DEMO.md`: exact demo commands
- `ARCHITECTURE.md`: detailed runtime design
- `SAFETY.md`: implemented guardrails and failure modes
- `SUBMISSION.md`: judge-facing one-pager
- `scripts/verify_submission.sh`: one-command verification
- `scripts/package_submission.sh`: local submission bundle creator

## Quick start

If you only want the restricted-environment demo:

```bash
python3 main.py demo
```

If you want the visual local dashboard:

```bash
python3 main.py ui --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

The dashboard supports two modes:

- `Offline Demo`: deterministic, no network required
- `NVIDIA NIM`: enter an API key, choose a hosted model, click `Connect NIM`, then start a run

If you want the unattended full run:

```bash
python3 main.py demo --auto-answer
```

If you want to demonstrate the guardrails directly:

```bash
python3 main.py guardrail-demo
```

## Example operator flow

1. Start a new run:

```bash
python3 main.py demo
```

2. Inspect the paused run:

```bash
python3 main.py status --run-id <RUN_ID>
```

3. Answer the checkpoint:

```bash
python3 main.py answer \
  --run-id <RUN_ID> \
  --checkpoint-id <CHECKPOINT_ID> \
  --decision request-liability-cap \
  --notes "Cap total liability at 12 months of fees."
```

4. Resume execution:

```bash
python3 main.py run --run-id <RUN_ID>
```

5. Print the final report:

```bash
python3 main.py report --run-id <RUN_ID>
```

## How persistence works

Every important transition is persisted:

- run state snapshot
- checkpoint creation
- checkpoint response
- guardrail decision
- final report

This means the process can stop at any time and continue later with the same `run_id`.

## How “no manual intervention” is verified

Use:

```bash
python3 main.py demo --auto-answer
```

This mode still creates policy checkpoints, but it consumes bundled demo approvals so the run can complete unattended end-to-end.

## Visual dashboard

The repo also includes a browser-based local dashboard derived from the Downloads UI direction and wired to the actual SQLite runtime.

From the dashboard you can:

- list existing runs
- start new demo runs
- switch between offline and NVIDIA NIM inference
- enter an API key and connect to the hosted NIM endpoint
- choose a model before starting a live run
- inspect findings, events, and final reports
- answer pending checkpoints
- resume execution from the browser

The API key is kept in host process memory only. It is not written into `runtime/*.db`.

## How interrupt/resume is verified

Use:

```bash
python3 main.py demo
```

Then stop after the checkpoint is printed, and later continue with `status`, `answer`, and `run`. The stored state is independent of the current shell session.

## Live NIM usage

If network is available, you can either use the dashboard connection flow or the CLI.

Dashboard flow:

1. `python3 main.py ui --port 8765`
2. Open `http://127.0.0.1:8765`
3. Switch the inference card to `NVIDIA NIM`
4. Paste `NVIDIA_API_KEY`
5. Keep the default `https://integrate.api.nvidia.com/v1` base URL unless you are using a different OpenAI-compatible NIM endpoint
6. Choose a model and click `Connect NIM`
7. Start a run from the browser

CLI flow:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```

Supported environment variables:

- `NVIDIA_API_KEY`
- `NIM_BASE_URL` (optional, defaults to `https://integrate.api.nvidia.com/v1`)

Recommended hosted model IDs for the dashboard:

- `nvidia/nemotron-3-super-120b-a12b`
- `nvidia/nemotron-3-nano-30b-a3b`
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`

## Official NemoClaw alignment

This repo is NemoClaw-compatible, but it is not a replacement for the official `nemoclaw` CLI.

Current NVIDIA docs describe NemoClaw as the host-side stack that:

- creates an OpenClaw sandbox
- routes inference to the selected provider and model
- applies filesystem and network policy from the first boot

The practical mapping for this project is:

- this repo provides the long-agent workload, persistence layer, policy behavior, and dashboard
- NVIDIA NIM provides the hosted open-source model endpoint used by the live backend
- official NemoClaw can be used as the outer sandbox/orchestration layer when the final hackathon environment requires it

Current official quickstart commands documented by NVIDIA are:

```bash
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash
NEMOCLAW_PROVIDER=routed NVIDIA_API_KEY=<your-key> nemoclaw onboard --non-interactive
```

That means the most realistic submission path is:

1. demo this repo locally with the offline mode and the live NIM mode
2. explain that NemoClaw is the deployment and policy shell around the agent workload, not the internal logic engine itself

## Guardrail summary

Implemented policies:

- reject external network lookups in restricted mode
- reject arbitrary host file reads
- rewrite risky auto-decisions into human checkpoints
- reject finalization while checkpoints remain open
- label outputs as operational review, not legal advice

See [SAFETY.md](SAFETY.md) for the exact guardrail behavior.

## Verification

Run the built-in tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Legacy assets

The historical HTML and JSX demo files are preserved under [legacy/README.md](legacy/README.md). They are no longer the primary implementation path for the NemoClaw submission.
