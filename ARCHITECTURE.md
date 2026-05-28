# ARCHITECTURE

## Problem Definition

The agent solves a bounded but real HaaS operations task:

> Produce an actionable ops review for public help signals while forcing human involvement before external outreach, payout-sensitive actions, personalized finance content, or unsafe privacy decisions.

Success is measured by:

- public-signal leads reviewed from bundled scenario data
- high-risk leads flagged
- human gates enforced before outreach and reward-sensitive decisions
- durable state across interruption
- reproducible HaaS ops report generation

## State Machine

```text
created
  -> planning
  -> analyzing
      -> waiting_human
      -> analyzing
      -> synthesizing
  -> completed
```

State meanings:

- `created`: run exists, no work performed yet.
- `planning`: HaaS ops review plan is generated.
- `analyzing`: public-signal leads are processed one by one.
- `waiting_human`: a policy-rewritten decision requires operator input.
- `synthesizing`: findings are compiled into the final ops report.
- `completed`: the final report is stored and printable.

## Persistence Model

SQLite is the single durable store.

`runs` stores run id, scenario id, reasoner backend, target model, status, phase, latest state snapshot, and final report.

`checkpoints` stores checkpoint id, run id, lead id, human question, allowed options, status, chosen answer, and notes.

`events` stores an append-only audit trail for planning, lead analysis, guardrail decisions, checkpoint creation, checkpoint answers, and report completion.

## Planning and Execution Flow

```text
CLI or dashboard command
  -> load or create run
  -> load bundled HaaS scenario
  -> select reasoner backend
  -> execute one state-machine step
  -> evaluate policy for each proposed operation
  -> persist snapshot + event
  -> stop on checkpoint or completion
```

## Reasoner Abstraction

`scripted_nemotron`:

- deterministic offline demo path
- repeatable judging flow
- no dependency on network or hosted inference
- emits structured HaaS ops plans, lead findings, and final reports

`nim`:

- optional live Nemotron backend
- same interface as the offline reasoner
- uses NIM-compatible `POST /v1/chat/completions`
- not required for restricted demo

## Guardrail Position

```text
reasoner proposes action
  -> guardrail evaluates action
      -> allow
      -> reject
      -> rewrite
  -> engine persists result
```

The model can propose, but policy decides whether the proposal is executable. The engine cannot silently skip policy outcomes.

## Implemented Policy Patterns

Reject:

- external network lookups in restricted mode
- arbitrary host file reads
- finalization while unresolved checkpoints remain

Rewrite:

- high-risk marketplace decisions
- external outreach
- reward-sensitive actions
- personalized finance content that can become educational discussion

Rewrite target:

- `create_checkpoint`

## Memory Model

Durable memory includes:

- reviewed leads
- pending decisions
- answered checkpoints
- guardrail interventions
- final report text

This makes resume behavior deterministic even after the Python process exits.

## Why SQLite

SQLite is enough because this is a single-process demo, needs no dependency installation, is easy to reset and inspect, and is robust enough for interruption/resume.
