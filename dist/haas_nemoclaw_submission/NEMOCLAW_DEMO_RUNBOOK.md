# NemoClaw Demo Runbook

## Fastest judge flow

### Unattended path

```bash
python3 main.py demo --auto-answer
```

### Interactive persistence path

```bash
python3 main.py demo
python3 main.py status --run-id <RUN_ID>
python3 main.py answer --run-id <RUN_ID> --checkpoint-id <CHECKPOINT_ID> --decision request-liability-cap --notes "Cap total liability at 12 months of fees."
python3 main.py run --run-id <RUN_ID>
python3 main.py report --run-id <RUN_ID>
```

## What to emphasize

- The agent does useful work before asking for help.
- High-risk judgment calls are blocked by policy and turned into checkpoints.
- State survives process termination because it is stored in SQLite.
- The default demo requires no internet and no package install.

## Bonus path

```bash
python3 main.py guardrail-demo
```

This explicitly shows reject and rewrite behavior from the policy layer.
