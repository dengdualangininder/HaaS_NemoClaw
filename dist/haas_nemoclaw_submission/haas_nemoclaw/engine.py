from __future__ import annotations

from collections.abc import Iterable
from uuid import uuid4

from haas_nemoclaw.guardrails import GuardrailPolicy
from haas_nemoclaw.models import CheckpointRecord, ClauseFinding, RunState
from haas_nemoclaw.reasoners import BaseReasoner
from haas_nemoclaw.scenarios import get_scenario
from haas_nemoclaw.store import SQLiteStore


class LongAgentEngine:
    def __init__(
        self,
        store: SQLiteStore,
        reasoner: BaseReasoner | None,
        guardrails: GuardrailPolicy,
    ):
        self.store = store
        self.reasoner = reasoner
        self.guardrails = guardrails

    def create_run(self, scenario_id: str, auto_answer: bool) -> RunState:
        scenario = get_scenario(scenario_id)
        info = self.reasoner.info()
        run_state = RunState(
            run_id=f"run-{uuid4().hex[:10]}",
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            objective=scenario.objective,
            status="created",
            phase="planning",
            clause_index=0,
            plan=[],
            findings=[],
            reasoner_backend=info.backend,
            target_model=info.model_name,
            inference_base_url=info.base_url,
            auto_answer=auto_answer,
            metrics={
                "guardrail_interventions": 0,
                "human_checkpoints": 0,
                "high_risk_clauses": 0,
            },
        )
        self.store.create_run(run_state)
        self.store.add_event(
            run_state.run_id,
            "run_created",
            "Created new long-agent run.",
            {"scenario_id": scenario_id, "reasoner_backend": info.backend},
        )
        return run_state

    def load_run(self, run_id: str) -> RunState:
        return self.store.get_run(run_id)

    def answer_checkpoint(self, run_id: str, checkpoint_id: str, decision: str, notes: str = "") -> None:
        checkpoint = self.store.get_checkpoint(checkpoint_id)
        if checkpoint.run_id != run_id:
            raise ValueError("Checkpoint does not belong to the specified run.")
        if decision not in checkpoint.options:
            raise ValueError(
                f"Decision '{decision}' is invalid for checkpoint {checkpoint_id}. "
                f"Allowed options: {', '.join(checkpoint.options)}"
            )
        checkpoint.status = "answered"
        checkpoint.decision = decision
        checkpoint.notes = notes
        self.store.save_checkpoint(checkpoint)
        self.store.add_event(
            run_id,
            "checkpoint_answered",
            "Checkpoint answered by operator.",
            {
                "checkpoint_id": checkpoint_id,
                "decision": decision,
                "notes": notes,
            },
        )

    def run_until_blocked(self, run_id: str, max_steps: int = 100) -> RunState:
        run_state = self.store.get_run(run_id)
        step_count = 0
        while True:
            if run_state.status == "completed":
                break
            if run_state.status == "waiting_human" and self.store.count_open_checkpoints(run_id) > 0:
                break
            if step_count >= max_steps:
                break
            run_state = self._step(run_state)
            self.store.save_run(run_state)
            step_count += 1
        return run_state

    def _step(self, run_state: RunState) -> RunState:
        if self.reasoner is None:
            raise RuntimeError("A reasoner backend is required to execute run steps.")
        scenario = get_scenario(run_state.scenario_id)

        if run_state.phase == "planning":
            run_state.plan = self.reasoner.build_plan(scenario)
            run_state.status = "running"
            run_state.phase = "analyzing"
            self.store.add_event(
                run_state.run_id,
                "plan_created",
                "Created HaaS ops review plan.",
                {"plan": run_state.plan},
            )
            return run_state

        if run_state.phase == "analyzing":
            if run_state.clause_index >= len(scenario.clauses):
                run_state.phase = "synthesizing"
                return run_state

            clause = scenario.clauses[run_state.clause_index]
            if clause.risk_level >= 7:
                run_state.metrics["high_risk_clauses"] += 1

            finding = self.reasoner.analyze_clause(scenario, clause, run_state)
            run_state.findings.append(finding)
            self.store.add_event(
                run_state.run_id,
                "lead_analyzed",
                "Analyzed marketplace lead.",
                {"clause_id": clause.clause_id, "risk_level": clause.risk_level},
            )

            if self._apply_guardrails(run_state, finding):
                run_state.status = "waiting_human"
                run_state.phase = "waiting_human"
                run_state.clause_index += 1
                return run_state

            run_state.clause_index += 1
            return run_state

        if run_state.phase == "waiting_human":
            if self.store.count_open_checkpoints(run_state.run_id) == 0:
                run_state.status = "running"
                run_state.phase = "analyzing"
            return run_state

        if run_state.phase == "synthesizing":
            open_checkpoints = self.store.count_open_checkpoints(run_state.run_id)
            decision = self.guardrails.evaluate(
                operation=_finalize_operation(open_checkpoints=open_checkpoints)
            )
            self.store.add_event(
                run_state.run_id,
                "guardrail_checked",
                "Checked report finalization policy.",
                {"verdict": decision.verdict, "reason": decision.reason},
            )
            if decision.verdict != "allow":
                run_state.status = "waiting_human"
                run_state.phase = "waiting_human"
                run_state.metrics["guardrail_interventions"] += 1
                return run_state

            checkpoint_map = {
                checkpoint.checkpoint_id: {
                    "decision": checkpoint.decision or "",
                    "notes": checkpoint.notes or "",
                }
                for checkpoint in self.store.list_checkpoints(run_state.run_id)
            }
            run_state.final_report = self.reasoner.synthesize_report(
                scenario, run_state, checkpoint_map
            )
            run_state.status = "completed"
            run_state.phase = "completed"
            self.store.add_event(
                run_state.run_id,
                "run_completed",
                "Completed long-agent run and stored final report.",
                {"report_length": len(run_state.final_report)},
            )
            return run_state

        return run_state

    def _apply_guardrails(self, run_state: RunState, finding: ClauseFinding) -> bool:
        scenario = get_scenario(run_state.scenario_id)
        checkpoint_needed = False

        for operation in finding.proposed_operations:
            decision = self.guardrails.evaluate(operation)
            self.store.add_event(
                run_state.run_id,
                "guardrail_checked",
                "Evaluated proposed operation.",
                {
                    "operation": operation.to_dict(),
                    "verdict": decision.verdict,
                    "reason": decision.reason,
                },
            )
            if decision.verdict in {"reject", "rewrite"}:
                run_state.metrics["guardrail_interventions"] += 1
                finding.guardrail_notes.append(f"{decision.verdict.upper()}: {decision.reason}")

            if decision.verdict == "rewrite" and decision.rewritten_operation:
                checkpoint_needed = decision.rewritten_operation.kind == "create_checkpoint"

        if checkpoint_needed:
            checkpoint = CheckpointRecord(
                checkpoint_id=f"cp-{uuid4().hex[:8]}",
                run_id=run_state.run_id,
                clause_id=finding.clause_id,
                title=finding.title,
                question=finding.question,
                options=finding.options,
            )
            finding.checkpoint_id = checkpoint.checkpoint_id
            self.store.create_checkpoint(checkpoint)
            run_state.metrics["human_checkpoints"] += 1
            self.store.add_event(
                run_state.run_id,
                "checkpoint_created",
                "Created human approval checkpoint.",
                checkpoint.to_dict(),
            )
            if run_state.auto_answer:
                answer = scenario.demo_answers[finding.clause_id]
                checkpoint.status = "answered"
                checkpoint.decision = answer["decision"]
                checkpoint.notes = answer["notes"]
                self.store.save_checkpoint(checkpoint)
                self.store.add_event(
                    run_state.run_id,
                    "checkpoint_auto_answered",
                    "Answered checkpoint from bundled demo approvals.",
                    checkpoint.to_dict(),
                )
                return False
            return True

        return False


def _finalize_operation(open_checkpoints: int):
    from haas_nemoclaw.models import ProposedOperation

    return ProposedOperation(
        kind="finalize_report",
        summary="Finalize the HaaS ops report.",
        metadata={"open_checkpoints": open_checkpoints},
    )


def format_status(store: SQLiteStore, run_state: RunState) -> str:
    checkpoints = store.list_checkpoints(run_state.run_id)
    events = store.list_events(run_state.run_id)
    lines = [
        f"run_id: {run_state.run_id}",
        f"title: {run_state.title}",
        f"status: {run_state.status}",
        f"phase: {run_state.phase}",
        f"reasoner_backend: {run_state.reasoner_backend}",
        f"target_model: {run_state.target_model}",
        f"leads_processed: {run_state.clause_index}/{len(get_scenario(run_state.scenario_id).clauses)}",
        f"guardrail_interventions: {run_state.metrics.get('guardrail_interventions', 0)}",
        f"human_checkpoints: {run_state.metrics.get('human_checkpoints', 0)}",
        "",
        "pending_checkpoints:",
    ]
    pending = [checkpoint for checkpoint in checkpoints if checkpoint.status != "answered"]
    if not pending:
        lines.append("- none")
    else:
        for checkpoint in pending:
            lines.extend(
                [
                    f"- checkpoint_id: {checkpoint.checkpoint_id}",
                    f"  lead_id: {checkpoint.clause_id}",
                    f"  question: {checkpoint.question}",
                    f"  options: {', '.join(checkpoint.options)}",
                ]
            )

    lines.extend(["", "recent_events:"])
    for event in events[-5:]:
        lines.append(f"- [{event['ts']}] {event['kind']}: {event['message']}")

    return "\n".join(lines)


def format_runs(rows: Iterable[dict[str, str]]) -> str:
    rows = list(rows)
    if not rows:
        return "No runs found."
    lines = []
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row["run_id"],
                    row["scenario_id"],
                    row["status"],
                    row["phase"],
                    row["reasoner_backend"],
                    row["updated_at"],
                ]
            )
        )
    return "\n".join(lines)
