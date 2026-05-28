from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Clause:
    clause_id: str
    title: str
    text: str
    category: str
    risk_level: int
    summary: str
    recommendation: str
    requires_human: bool = False
    question: str = ""
    options: list[str] = field(default_factory=list)
    unsafe_operations: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    scenario_id: str
    title: str
    objective: str
    operator_profile: dict[str, Any]
    clauses: list[Clause]
    demo_answers: dict[str, dict[str, str]]


@dataclass
class ProposedOperation:
    kind: str
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GuardrailDecision:
    verdict: str
    reason: str
    rewritten_operation: ProposedOperation | None = None


@dataclass
class ClauseFinding:
    clause_id: str
    title: str
    category: str
    risk_level: int
    summary: str
    recommendation: str
    requires_human: bool
    question: str
    options: list[str]
    proposed_operations: list[ProposedOperation] = field(default_factory=list)
    guardrail_notes: list[str] = field(default_factory=list)
    checkpoint_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["proposed_operations"] = [op.to_dict() for op in self.proposed_operations]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClauseFinding":
        payload = dict(data)
        payload["proposed_operations"] = [
            ProposedOperation(**item) for item in payload.get("proposed_operations", [])
        ]
        return cls(**payload)


@dataclass
class CheckpointRecord:
    checkpoint_id: str
    run_id: str
    clause_id: str
    title: str
    question: str
    options: list[str]
    status: str = "pending"
    decision: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CheckpointRecord":
        return cls(**data)


@dataclass
class RunState:
    run_id: str
    scenario_id: str
    title: str
    objective: str
    status: str
    phase: str
    clause_index: int
    plan: list[dict[str, Any]]
    findings: list[ClauseFinding]
    reasoner_backend: str
    target_model: str
    inference_base_url: str
    auto_answer: bool
    final_report: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["findings"] = [finding.to_dict() for finding in self.findings]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunState":
        payload = dict(data)
        payload["findings"] = [
            ClauseFinding.from_dict(item) for item in payload.get("findings", [])
        ]
        payload.setdefault("inference_base_url", "")
        return cls(**payload)
