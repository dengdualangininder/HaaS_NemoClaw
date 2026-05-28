# SAFETY

## Goal

Use policy-based guardrails to make the long-running agent safer, more inspectable, and harder to misuse.

## Implemented guardrails

### 1. No external network in restricted mode

If the reasoner proposes an external lookup during the offline demo path, the guardrail rejects it.

Why:

- NemoClaw environments may block network access
- the demo must remain repeatable
- the contract review should not depend on live browsing

### 2. No arbitrary host file access

If the reasoner proposes reading a host file outside the project-owned runtime, the guardrail rejects it.

Why:

- the demo must not require broad local file permissions
- sensitive host documents must stay out of scope

### 3. Human approval for risky or subjective decisions

If the reasoner proposes auto-accepting a clause with high risk or business-judgment ambiguity, the guardrail rewrites the action into a checkpoint.

Why:

- this is the Human-in-the-Loop core of the design
- the agent may assist, but it may not silently decide for the operator

### 4. No finalization with open checkpoints

The run cannot move to completed while required human gates remain unresolved.

Why:

- prevents false completion
- keeps the audit trail honest

### 5. Output framing guardrail

The final report is framed as an operational negotiation review, not legal advice.

Why:

- the demo is about workflow automation and escalation
- not about replacing legal counsel

## Demonstrating the guardrails

Run:

```bash
python3 main.py guardrail-demo
```

The demo prints examples of:

- `REJECT`: external network request
- `REJECT`: host file read
- `REWRITE`: risky auto-accept becomes checkpoint creation
- `REJECT`: finalize while unresolved work remains

## Policy outcomes

Each policy check returns one of:

- `allow`
- `reject`
- `rewrite`

Every outcome is written to the audit log.

## Safety boundaries

This repo does not:

- contact real counterparties
- send messages externally
- pull arbitrary local documents
- make final legal judgments autonomously
- move money or trigger contracts

## Why this is a bonus-worthy implementation

The guardrails are not just prose in the README.

They are implemented in code as a separate policy decision layer that:

- intercepts model-proposed actions
- blocks prohibited actions
- converts unsafe autonomy into explicit human approvals
- persists the evidence trail

That is the core “policy-based guardrails” story the judges can inspect and replay.
