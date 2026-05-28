from __future__ import annotations

import argparse
from pathlib import Path
from sys import exit as sys_exit

from haas_nemoclaw.engine import LongAgentEngine, format_runs, format_status
from haas_nemoclaw.guardrails import GuardrailPolicy, demo_operations
from haas_nemoclaw.reasoners import DEFAULT_NIM_MODEL, build_reasoner
from haas_nemoclaw.scenarios import DEMO_SCENARIO
from haas_nemoclaw.store import SQLiteStore
from haas_nemoclaw.dashboard import serve_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="haas-nemoclaw",
        description="Offline-first NemoClaw long-agent demo with persistence and guardrails.",
    )
    parser.add_argument(
        "--db",
        default="runtime/haas_nemoclaw.db",
        help="SQLite database path for persistent runtime state.",
    )
    parser.add_argument(
        "--reasoner",
        default="scripted_nemotron",
        choices=("scripted_nemotron", "nim"),
        help="Reasoner backend to use for new runs.",
    )
    parser.add_argument(
        "--nim-model",
        default=DEFAULT_NIM_MODEL,
        help="Model name for the live NIM backend or the offline Nemotron contract label.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_cmd = subparsers.add_parser("demo", help="Create a new demo run and execute until blocked or completed.")
    demo_cmd.add_argument(
        "--scenario",
        default=DEMO_SCENARIO.scenario_id,
        help="Bundled demo scenario id.",
    )
    demo_cmd.add_argument(
        "--auto-answer",
        action="store_true",
        help="Use bundled approvals so the run completes unattended.",
    )
    demo_cmd.set_defaults(func=command_demo)

    start_cmd = subparsers.add_parser("start", help="Create a run without executing it.")
    start_cmd.add_argument("--scenario", default=DEMO_SCENARIO.scenario_id)
    start_cmd.add_argument("--auto-answer", action="store_true")
    start_cmd.set_defaults(func=command_start)

    run_cmd = subparsers.add_parser("run", help="Resume a run until blocked or completed.")
    run_cmd.add_argument("--run-id", required=True)
    run_cmd.set_defaults(func=command_run)

    status_cmd = subparsers.add_parser("status", help="Show persisted run state.")
    status_cmd.add_argument("--run-id", required=True)
    status_cmd.set_defaults(func=command_status)

    report_cmd = subparsers.add_parser("report", help="Print the final report for a completed run.")
    report_cmd.add_argument("--run-id", required=True)
    report_cmd.set_defaults(func=command_report)

    answer_cmd = subparsers.add_parser("answer", help="Answer a human checkpoint.")
    answer_cmd.add_argument("--run-id", required=True)
    answer_cmd.add_argument("--checkpoint-id", required=True)
    answer_cmd.add_argument("--decision", required=True)
    answer_cmd.add_argument("--notes", default="")
    answer_cmd.set_defaults(func=command_answer)

    runs_cmd = subparsers.add_parser("runs", help="List all persisted runs.")
    runs_cmd.set_defaults(func=command_runs)

    guardrail_cmd = subparsers.add_parser("guardrail-demo", help="Show policy-based guardrail behavior.")
    guardrail_cmd.set_defaults(func=command_guardrail_demo)

    ui_cmd = subparsers.add_parser("ui", help="Run a local visual dashboard for the long-agent runtime.")
    ui_cmd.add_argument("--host", default="127.0.0.1")
    ui_cmd.add_argument("--port", type=int, default=8765)
    ui_cmd.set_defaults(func=command_ui)

    args = parser.parse_args()
    return args.func(args)


def build_store(args) -> SQLiteStore:
    return SQLiteStore(Path(args.db))


def build_engine_for_new_run(args) -> tuple[SQLiteStore, LongAgentEngine]:
    store = build_store(args)
    reasoner = build_reasoner(args.reasoner, model_name=args.nim_model)
    engine = LongAgentEngine(store=store, reasoner=reasoner, guardrails=GuardrailPolicy())
    return store, engine


def build_engine_for_existing_run(args, run_id: str) -> tuple[SQLiteStore, LongAgentEngine]:
    store = build_store(args)
    run_state = store.get_run(run_id)
    reasoner = build_reasoner(
        run_state.reasoner_backend,
        model_name=run_state.target_model,
        base_url=run_state.inference_base_url or None,
    )
    engine = LongAgentEngine(store=store, reasoner=reasoner, guardrails=GuardrailPolicy())
    return store, engine


def command_demo(args) -> int:
    store, engine = build_engine_for_new_run(args)
    run_state = engine.create_run(args.scenario, auto_answer=args.auto_answer)
    run_state = engine.run_until_blocked(run_state.run_id)
    print(format_status(store, run_state))
    print("")
    print(next_steps(store, run_state))
    return 0


def command_start(args) -> int:
    store, engine = build_engine_for_new_run(args)
    run_state = engine.create_run(args.scenario, auto_answer=args.auto_answer)
    print(f"Created run: {run_state.run_id}")
    print(format_status(store, run_state))
    return 0


def command_run(args) -> int:
    store, engine = build_engine_for_existing_run(args, args.run_id)
    run_state = engine.run_until_blocked(args.run_id)
    print(format_status(store, run_state))
    print("")
    print(next_steps(store, run_state))
    return 0


def command_status(args) -> int:
    store = build_store(args)
    run_state = store.get_run(args.run_id)
    print(format_status(store, run_state))
    print("")
    print(next_steps(store, run_state))
    return 0


def command_report(args) -> int:
    store = build_store(args)
    run_state = store.get_run(args.run_id)
    if not run_state.final_report:
        print("Run has no final report yet. Resume the run or answer pending checkpoints first.")
        return 1
    print(run_state.final_report)
    return 0


def command_answer(args) -> int:
    store = build_store(args)
    engine = LongAgentEngine(store=store, reasoner=None, guardrails=GuardrailPolicy())
    engine.answer_checkpoint(args.run_id, args.checkpoint_id, args.decision, args.notes)
    print(f"Answered checkpoint {args.checkpoint_id} for run {args.run_id}.")
    return 0


def command_runs(args) -> int:
    store = build_store(args)
    print(format_runs(store.list_runs()))
    return 0


def command_guardrail_demo(args) -> int:
    guardrails = GuardrailPolicy()
    for operation in demo_operations():
        decision = guardrails.evaluate(operation)
        print(f"operation: {operation.kind}")
        print(f"summary: {operation.summary}")
        print(f"verdict: {decision.verdict}")
        print(f"reason: {decision.reason}")
        if decision.rewritten_operation:
            print(f"rewritten_to: {decision.rewritten_operation.kind}")
        print("")
    return 0


def command_ui(args) -> int:
    serve_dashboard(
        db_path=Path(args.db),
        host=args.host,
        port=args.port,
        default_reasoner=args.reasoner,
        nim_model=args.nim_model,
    )
    return 0


def next_steps(store, run_state) -> str:
    pending = [checkpoint for checkpoint in store.list_checkpoints(run_state.run_id) if checkpoint.status != "answered"]
    if run_state.status == "completed":
        return f"Next: python3 main.py report --run-id {run_state.run_id}"
    if run_state.status == "waiting_human" and pending:
        return (
            f"Next: answer the pending checkpoint, then run "
            f"`python3 main.py run --run-id {run_state.run_id}`"
        )
    return f"Next: python3 main.py run --run-id {run_state.run_id}"


if __name__ == "__main__":
    sys_exit(main())
