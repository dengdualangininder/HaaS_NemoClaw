from __future__ import annotations

from haas_nemoclaw.models import GuardrailDecision, ProposedOperation


class GuardrailPolicy:
    """Policy layer that accepts, rejects, or rewrites proposed actions."""

    def evaluate(self, operation: ProposedOperation) -> GuardrailDecision:
        kind = operation.kind
        metadata = operation.metadata

        if kind == "network_lookup":
            return GuardrailDecision(
                verdict="reject",
                reason="Restricted NemoClaw demo mode disallows external network lookups.",
            )

        if kind == "read_host_file":
            return GuardrailDecision(
                verdict="reject",
                reason="Arbitrary host file reads are disallowed; use bundled operator context only.",
            )

        if kind == "auto_accept_clause" and (
            metadata.get("risk_level", 0) >= 7 or metadata.get("requires_human", False)
        ):
            return GuardrailDecision(
                verdict="rewrite",
                reason="Risky or subjective clause decisions must be routed through a human checkpoint.",
                rewritten_operation=ProposedOperation(
                    kind="create_checkpoint",
                    summary="Route clause decision to human approval.",
                    metadata=metadata,
                ),
            )

        if kind == "finalize_report" and metadata.get("open_checkpoints", 0) > 0:
            return GuardrailDecision(
                verdict="reject",
                reason="The report cannot be finalized while required checkpoints remain open.",
            )

        return GuardrailDecision(verdict="allow", reason="Operation is within policy.")


def demo_operations() -> list[ProposedOperation]:
    return [
        ProposedOperation(
            kind="network_lookup",
            summary="Look up market-standard liability caps on the public web.",
        ),
        ProposedOperation(
            kind="read_host_file",
            summary="Read /Users/operator/Documents/customer-playbook.md for extra context.",
        ),
        ProposedOperation(
            kind="auto_accept_clause",
            summary="Auto-accept unlimited liability clause.",
            metadata={"risk_level": 9, "requires_human": True},
        ),
        ProposedOperation(
            kind="finalize_report",
            summary="Finalize the report before all approvals are resolved.",
            metadata={"open_checkpoints": 1},
        ),
    ]
