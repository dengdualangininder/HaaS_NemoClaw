# DEMO

## Primary restricted-environment demo

This is the recommended NemoClaw judging flow because it does not require internet access or arbitrary host file reads.

## Visual local demo

If you want to see the system in a browser instead of only in the terminal:

```bash
python3 main.py ui --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

Recommended click path:

1. Click `Start Demo Run`
2. Open the newest run from the left column
3. Inspect the pending checkpoint on the right
4. Submit a decision
5. Click `Resume Run`
6. Repeat until the report appears in the center panel

## Live NIM dashboard demo

If you want to prove the agent can use NVIDIA-hosted open-source models:

1. Start the dashboard:

```bash
python3 main.py ui --port 8765
```

2. Open `http://127.0.0.1:8765`
3. In the `Inference` panel, select `NVIDIA NIM`
4. Enter `NVIDIA_API_KEY`
5. Keep the base URL as `https://integrate.api.nvidia.com/v1`
6. Pick a model such as `nvidia/nemotron-3-super-120b-a12b`
7. Click `Connect NIM`
8. Click `Start Demo Run`
9. Show that the selected run now displays `NVIDIA NIM` in the `Engine` metric and the chosen model in the `Runtime` section

What to point out:

- The only manual secret step is pasting the API key
- The key is not stored in SQLite
- The long-agent state machine and guardrails are unchanged; only the reasoning backend changes

### 1. Start a new run

```bash
python3 main.py demo
```

Expected result:

- A new `run_id`
- Clause analysis begins
- The agent pauses at the first high-risk decision
- A `checkpoint_id` is printed

### 2. Show persisted state

```bash
python3 main.py status --run-id <RUN_ID>
```

What to point out:

- The run is still present even after the previous command ended
- The agent knows which clause it reached
- The pending checkpoint is listed explicitly
- Guardrail events are already recorded

### 3. Answer the first checkpoint

```bash
python3 main.py answer \
  --run-id <RUN_ID> \
  --checkpoint-id <CHECKPOINT_ID> \
  --decision request-liability-cap \
  --notes "Cap total liability at 12 months of fees."
```

### 4. Resume the run

```bash
python3 main.py run --run-id <RUN_ID>
```

Expected result:

- The agent resumes from the stored state
- It continues clause analysis
- It may pause again if another human judgment gate is required

### 5. Repeat until completion

Use `status`, `answer`, and `run` until the run reaches `completed`.

### 6. Print the final report

```bash
python3 main.py report --run-id <RUN_ID>
```

## Unattended completion demo

To prove the long task can complete without live intervention:

```bash
python3 main.py demo --auto-answer
```

What this demonstrates:

- The same checkpoints are created
- Demo approvals are injected automatically from bundled scenario data
- The full run completes without operator typing during execution

## Interrupt and resume demo

To explicitly show persistence:

1. Start with `python3 main.py demo`
2. Stop after the checkpoint appears
3. Wait or open a new shell
4. Run `python3 main.py status --run-id <RUN_ID>`
5. Continue with `answer` and `run`

This proves the state is not held only in memory.

## Guardrail bonus demo

Show policy-based refusal and rewrite behavior:

```bash
python3 main.py guardrail-demo
```

Expected output includes:

- a rejected external network request
- a rejected host file read
- a rewritten risky auto-accept decision into a human checkpoint
- a rejected finalize action while work is still pending

## Live Nemotron demo

If you prefer CLI instead of the browser:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```

This uses the same long-agent flow, but swaps the offline adapter for a live Nemotron backend.

## Judge script summary

If the reviewer has 2 minutes:

1. `python3 main.py demo`
2. `python3 main.py status --run-id <RUN_ID>`
3. `python3 main.py answer ...`
4. `python3 main.py run --run-id <RUN_ID>`
5. `python3 main.py guardrail-demo`

If the reviewer has 30 seconds:

1. `python3 main.py demo --auto-answer`
2. `python3 main.py report --run-id <RUN_ID>`
