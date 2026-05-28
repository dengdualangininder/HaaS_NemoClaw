# SAFETY

## Guardrail Goals

The agent may propose HaaS operations, but policy decides whether those operations are executable.

The safety layer prevents the demo from silently:

- browsing the web in restricted mode
- reading arbitrary host files
- contacting external users
- exposing private data
- giving personalized financial advice
- moving real funds
- finalizing reports while approvals remain open

## Implemented Policies

### 1. No External Lookup in Restricted Mode

`network_lookup` is rejected. The demo uses bundled public-signal data.

### 2. No Arbitrary Host File Reads

`read_host_file` is rejected. Operator context must come from bundled scenario data or project-owned runtime state.

### 3. External Outreach Is Approval-Gated

`external_outreach` is rewritten into a human checkpoint. NemoClaw may prepare invite drafts, but cannot automatically DM, reply, or post to external platforms.

### 4. Reward Actions Are Proposal-Only

`move_funds` is rewritten into a human checkpoint. NemoClaw may propose XP or payout outcomes, but cannot move real funds or write to a production ledger.

### 5. High-Risk Marketplace Decisions Need Human Checkpoints

High-risk or subjective marketplace approvals are rewritten into `create_checkpoint`.

### 6. No Finalization with Open Checkpoints

`finalize_report` is rejected while required approvals remain unresolved.

## Demo Safety Cases

Low-risk sensory task:

- Allowed as a task draft.

External author invite:

- Rewritten into a draft-only approval checkpoint.

Private address / confrontation request:

- Blocked by the scenario recommendation and guardrail audit trail; no task should be created.

Personalized stock pick:

- Rewritten into general educational market-risk discussion.

Reward proposal:

- Kept proposal-only; real payout remains approval-gated.

## Output Framing

Final output is an operational HaaS marketplace review and escalation aid. It is not financial, legal, medical, or safety advice.
