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
python3 main.py answer --run-id <RUN_ID> --checkpoint-id <CHECKPOINT_ID> --decision approve-draft-only-invite --notes "Keep outreach draft-only until HaaS Ops approves the connector path."
python3 main.py run --run-id <RUN_ID>
python3 main.py report --run-id <RUN_ID>
```

## What to emphasize

- The agent does useful work before asking for help.
- External outreach, finance rewrite, and reward proposal decisions are blocked by policy and turned into checkpoints.
- Doxxing, private contact data, and confrontation requests are refused instead of taskified.
- State survives process termination because it is stored in SQLite.
- The default demo requires no internet and no package install.

## Bonus path

```bash
python3 main.py guardrail-demo
```

This explicitly shows reject and rewrite behavior from the policy layer.
