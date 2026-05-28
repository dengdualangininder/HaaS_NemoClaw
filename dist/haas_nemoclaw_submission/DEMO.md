# DEMO

## Primary Restricted-Environment Demo

Recommended NemoClaw judging path:

```bash
python3 main.py demo
```

Expected result:

- a new `run_id`
- HaaS ops planning begins
- public-signal leads are analyzed
- the agent pauses at the first human approval checkpoint
- a `checkpoint_id` is printed

## Visual Local Demo

```bash
python3 main.py ui --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

Recommended click path:

1. Click `Start Demo Run`.
2. Open the newest run from the left column.
3. Inspect the pending checkpoint on the right.
4. Submit an operator decision.
5. Click `Resume Run`.
6. Repeat until the HaaS ops report appears in the center panel.

## Persistence Proof

1. Start a new run:

```bash
python3 main.py demo
```

2. Show persisted state:

```bash
python3 main.py status --run-id <RUN_ID>
```

3. Answer the first checkpoint:

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

5. Repeat until complete, then print:

```bash
python3 main.py report --run-id <RUN_ID>
```

## Unattended Completion Demo

```bash
python3 main.py demo --auto-answer
```

This still creates policy checkpoints, but consumes bundled demo approvals so the run can complete without live typing.

## Guardrail Bonus Demo

```bash
python3 main.py guardrail-demo
```

Expected output includes:

- rejected external network lookup
- rejected host file read
- rewritten high-risk auto-approval into a human checkpoint
- rejected finalization while work remains pending

## Live NIM Dashboard Demo

If networking is allowed:

1. Start the dashboard:

```bash
python3 main.py ui --port 8765
```

2. Open `http://127.0.0.1:8765`.
3. Select `NVIDIA NIM`.
4. Enter `NVIDIA_API_KEY`.
5. Keep `https://integrate.api.nvidia.com/v1`.
6. Pick `nvidia/nemotron-3-super-120b-a12b`.
7. Click `Connect NIM`.
8. Click `Start Demo Run`.

The state machine and guardrails are unchanged; only the reasoner backend changes.
