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
                reason="Restricted NemoClaw demo mode disallows external network lookups; use bundled public-signal context.",
            )

        if kind == "read_host_file":
            return GuardrailDecision(
                verdict="reject",
                reason="Arbitrary host file reads are disallowed; use bundled operator context only.",
            )

        if kind == "external_outreach":
            return GuardrailDecision(
                verdict="rewrite",
                reason="External outreach must remain draft-only until a human operator or approved connector authorizes it.",
                rewritten_operation=ProposedOperation(
                    kind="create_checkpoint",
                    summary="Route external outreach decision to HaaS Ops approval.",
                    metadata=metadata,
                ),
            )

        if kind == "move_funds":
            return GuardrailDecision(
                verdict="rewrite",
                reason="NemoClaw may create reward proposals but cannot move real funds without ledger approval.",
                rewritten_operation=ProposedOperation(
                    kind="create_checkpoint",
                    summary="Route payout-sensitive action to HaaS Ops approval.",
                    metadata=metadata,
                ),
            )

        if kind == "auto_accept_clause" and metadata.get("category") == "privacy_safety":
            return GuardrailDecision(
                verdict="reject",
                reason="Privacy, doxxing, stalking, or confrontation requests must be refused instead of taskified.",
            )

        if kind == "auto_accept_clause" and (
            metadata.get("risk_level", 0) >= 7 or metadata.get("requires_human", False)
        ):
            return GuardrailDecision(
                verdict="rewrite",
                reason="Risky or subjective marketplace decisions must be routed through a human checkpoint.",
                rewritten_operation=ProposedOperation(
                    kind="create_checkpoint",
                    summary="Route HaaS ops decision to human approval.",
                    metadata=metadata,
                ),
            )

        if kind == "finalize_report" and metadata.get("open_checkpoints", 0) > 0:
            return GuardrailDecision(
                verdict="reject",
                reason="The ops report cannot be finalized while required checkpoints remain open.",
            )

        return GuardrailDecision(verdict="allow", reason="Operation is within policy.")


def demo_operations() -> list[ProposedOperation]:
    return [
        ProposedOperation(
            kind="network_lookup",
            summary="Search the public web for more Threads leads in restricted demo mode.",
        ),
        ProposedOperation(
            kind="read_host_file",
            summary="Read /Users/operator/Documents/private-user-list.csv for extra context.",
        ),
        ProposedOperation(
            kind="auto_accept_clause",
            summary="Auto-approve high-risk external outreach.",
            metadata={"risk_level": 9, "requires_human": True},
        ),
        ProposedOperation(
            kind="finalize_report",
            summary="Finalize the ops report before all approvals are resolved.",
            metadata={"open_checkpoints": 1},
        ),
    ]
