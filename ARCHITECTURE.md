# ARCHITECTURE

## Problem definition

The agent solves a bounded but real task:

> Produce an actionable negotiation review for a SaaS vendor contract while forcing human involvement at subjective or high-risk decision points.

Success is measured by:

- risk clauses identified correctly from bundled scenario data
- human gates enforced before sensitive decisions
- durable state across interruption
- reproducible final report generation

## State machine

```text
created
  -> planning
  -> analyzing
      -> waiting_human
      -> analyzing
      -> synthesizing
  -> completed
```

### State meanings

- `created`: run exists, no work performed yet
- `planning`: review plan is generated
- `analyzing`: clauses are processed one by one
- `waiting_human`: a policy-rewritten decision requires operator input
- `synthesizing`: findings are compiled into the final report
- `completed`: the final report is stored and printable

## Persistence model

SQLite is the single durable store.

### `runs`

Stores:

- run id
- scenario id
- reasoner backend
- target model
- status and phase
- latest state snapshot
- final report

### `checkpoints`

Stores:

- checkpoint id
- linked run id
- human question
- allowed options
- status
- chosen answer and notes

### `events`

Append-only audit trail for:

- plan creation
- clause analysis
- guardrail decisions
- checkpoint creation
- checkpoint response
- report completion

## Planning and execution flow

```text
CLI command
  -> load or create run
  -> load scenario
  -> select reasoner backend
  -> execute state-machine step
  -> evaluate policy for each proposed operation
  -> persist snapshot + event
  -> stop on checkpoint or completion
```

## Reasoner abstraction

### `scripted_nemotron`

Purpose:

- deterministic offline demo path
- repeatable judging flow
- no dependency on network or hosted inference

Behavior:

- emits a structured plan
- analyzes clauses using bundled scenario metadata
- proposes operations that the guardrail layer can inspect
- synthesizes a final report

### `nim`

Purpose:

- optional live Nemotron backend
- same interface as the offline reasoner

Behavior:

- uses NIM-compatible `POST /v1/chat/completions`
- expects JSON output for clause analysis and report synthesis
- is not required for the default restricted-environment demo

## Guardrail position in the stack

The guardrail layer sits between the reasoner and the engine.

```text
reasoner proposes action
  -> guardrail evaluates action
      -> allow
      -> reject
      -> rewrite
  -> engine persists result
```

This is the repo’s concrete mapping of the NemoClaw idea:

- the model can propose
- policy decides whether that proposal is executable
- the engine cannot silently skip policy outcomes

## Implemented policy patterns

### Reject

Used for:

- external network lookups in restricted mode
- host filesystem reads outside app-owned runtime state
- finalization while unresolved checkpoints remain

### Rewrite

Used for:

- high-risk auto-accept decisions
- subjective business judgment calls

Rewrite target:

- `create_checkpoint`

## Memory model

This project intentionally separates:

- transient reasoning context
- durable operational state

Durable memory includes:

- reviewed clauses
- pending decisions
- answered checkpoints
- guardrail interventions
- final report text

This makes resume behavior deterministic even after the Python process exits.

## Why no arbitrary file access

The demo does not ask the agent to open user-provided local files because that conflicts with the stated NemoClaw constraint.

Instead, the demo uses:

- bundled scenario content
- bundled operator policy defaults
- project-owned runtime state

This keeps the demo faithful to a restricted sandbox while still demonstrating long-running autonomy.

## Why SQLite instead of an external service

SQLite is enough here because:

- single-process demo
- no dependency installation
- easy reset and inspection
- robust enough for interruption/resume

It also directly supports the competition goal of a deployable agent on personal hardware.
