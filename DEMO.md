# DEMO

## Primary restricted-environment demo

This is the recommended NemoClaw judging flow because it does not require internet access or arbitrary host file reads.

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

If you have NIM access:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/llama-3.3-nemotron-super-49b-v1
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
