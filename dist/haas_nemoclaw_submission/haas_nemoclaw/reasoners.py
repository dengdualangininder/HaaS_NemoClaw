from __future__ import annotations

import json
import os
import ssl
import subprocess
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from haas_nemoclaw.models import Clause, ClauseFinding, ProposedOperation, RunState, Scenario


DEFAULT_NIM_MODEL = "nvidia/nemotron-3-super-120b-a12b"
DEFAULT_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
RECOMMENDED_NIM_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/nemotron-3-nano-30b-a3b",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
]


@dataclass
class ReasonerInfo:
    backend: str
    model_name: str
    base_url: str = ""


class BaseReasoner:
    def info(self) -> ReasonerInfo:
        raise NotImplementedError

    def build_plan(self, scenario: Scenario) -> list[dict[str, Any]]:
        raise NotImplementedError

    def analyze_clause(self, scenario: Scenario, clause: Clause, run_state: RunState) -> ClauseFinding:
        raise NotImplementedError

    def synthesize_report(
        self, scenario: Scenario, run_state: RunState, checkpoint_map: dict[str, dict[str, str]]
    ) -> str:
        raise NotImplementedError


def recommended_nim_models() -> list[str]:
    return list(RECOMMENDED_NIM_MODELS)


def _default_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    try:
        import certifi  # type: ignore
    except ImportError:
        return context
    context.load_verify_locations(cafile=certifi.where())
    return context


class ScriptedNemotronReasoner(BaseReasoner):
    def __init__(self, model_name: str = DEFAULT_NIM_MODEL):
        self.model_name = model_name

    def info(self) -> ReasonerInfo:
        return ReasonerInfo(backend="scripted_nemotron", model_name=self.model_name)

    def build_plan(self, scenario: Scenario) -> list[dict[str, Any]]:
        return [
            {
                "step": "intake",
                "goal": "Load bundled HaaS public-signal queue and operator policy profile.",
            },
            {
                "step": "risk_scan",
                "goal": "Inspect each marketplace lead and classify risk using deterministic policy rules.",
            },
            {
                "step": "human_gates",
                "goal": "Pause before outreach, payout-sensitive, or high-risk marketplace decisions.",
            },
            {
                "step": "final_report",
                "goal": "Produce a HaaS ops action list with an auditable decision trail.",
            },
        ]

    def analyze_clause(self, scenario: Scenario, clause: Clause, run_state: RunState) -> ClauseFinding:
        operations = [
            ProposedOperation(
                kind="auto_accept_clause",
                summary=f"Decide whether to approve marketplace item {clause.clause_id} automatically.",
                metadata={
                    "clause_id": clause.clause_id,
                    "category": clause.category,
                    "risk_level": clause.risk_level,
                    "requires_human": clause.requires_human,
                },
            )
        ]

        for unsafe_operation in clause.unsafe_operations:
            if unsafe_operation == "network_lookup":
                operations.append(
                    ProposedOperation(
                        kind="network_lookup",
                        summary="Fetch more public social posts from the live web.",
                        metadata={"clause_id": clause.clause_id},
                    )
                )
            elif unsafe_operation == "read_host_file":
                operations.append(
                    ProposedOperation(
                        kind="read_host_file",
                        summary="Read a host-side customer playbook outside the sandbox.",
                        metadata={"clause_id": clause.clause_id},
                    )
                )
            elif unsafe_operation == "external_outreach":
                operations.append(
                    ProposedOperation(
                        kind="external_outreach",
                        summary="Send or publish an external invite without operator approval.",
                        metadata={"clause_id": clause.clause_id},
                    )
                )
            elif unsafe_operation == "move_funds":
                operations.append(
                    ProposedOperation(
                        kind="move_funds",
                        summary="Release a real payout instead of creating a proposal-only reward.",
                        metadata={"clause_id": clause.clause_id},
                    )
                )

        return ClauseFinding(
            clause_id=clause.clause_id,
            title=clause.title,
            category=clause.category,
            risk_level=clause.risk_level,
            summary=clause.summary,
            recommendation=clause.recommendation,
            requires_human=clause.requires_human,
            question=clause.question,
            options=list(clause.options),
            proposed_operations=operations,
        )

    def synthesize_report(
        self, scenario: Scenario, run_state: RunState, checkpoint_map: dict[str, dict[str, str]]
    ) -> str:
        lines = [
            f"# {scenario.title}",
            "",
            "## Objective",
            scenario.objective,
            "",
            "## Outcome Summary",
            f"- Marketplace leads reviewed: {len(run_state.findings)} / {len(scenario.clauses)}",
            f"- High-risk leads: {run_state.metrics.get('high_risk_clauses', 0)}",
            f"- Human checkpoints: {run_state.metrics.get('human_checkpoints', 0)}",
            f"- Guardrail interventions: {run_state.metrics.get('guardrail_interventions', 0)}",
            "",
            "## Lead Decisions",
        ]

        for finding in run_state.findings:
            lines.append(f"### {finding.title} ({finding.clause_id})")
            lines.append(f"- Category: {finding.category}")
            lines.append(f"- Risk: {finding.risk_level}/10")
            lines.append(f"- Summary: {finding.summary}")
            lines.append(f"- Recommendation: {finding.recommendation}")
            if finding.guardrail_notes:
                lines.append(
                    "- Guardrails: " + " | ".join(note.replace("\n", " ") for note in finding.guardrail_notes)
                )
            if finding.checkpoint_id:
                response = checkpoint_map.get(finding.checkpoint_id, {})
                lines.append(f"- Human decision: {response.get('decision', 'pending')}")
                notes = response.get("notes")
                if notes:
                    lines.append(f"- Human notes: {notes}")
            else:
                lines.append("- Human decision: not required")
            lines.append("")

        lines.extend(
            [
                "## HaaS Ops Actions",
                "- Sensory lead: draft a low-risk bounty with a concrete verification rubric.",
                "- Outreach: keep author contact as draft-only until HaaS Ops approves the connector path.",
                "- Privacy/safety: refuse doxxing or confrontation requests and preserve an audit event.",
                "- Finance: rewrite personalized trading advice into general educational risk discussion.",
                "- Reward: create proposal-only XP rewards; keep real payout behind ledger approval.",
                "",
                "## Safety Note",
                "This output is an operational HaaS marketplace review and escalation aid, not financial, legal, or safety advice.",
            ]
        )
        return "\n".join(lines)


class NimNemotronReasoner(BaseReasoner):
    def __init__(
        self,
        model_name: str = DEFAULT_NIM_MODEL,
        base_url: str = DEFAULT_NIM_BASE_URL,
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY is required when using the nim reasoner backend.")

    def info(self) -> ReasonerInfo:
        return ReasonerInfo(backend="nim", model_name=self.model_name, base_url=self.base_url)

    def build_plan(self, scenario: Scenario) -> list[dict[str, Any]]:
        return ScriptedNemotronReasoner(model_name=self.model_name).build_plan(scenario)

    def analyze_clause(self, scenario: Scenario, clause: Clause, run_state: RunState) -> ClauseFinding:
        prompt = {
            "task": "Analyze a HaaS marketplace lead for taskability, safety, and operations risk.",
            "scenario_title": scenario.title,
            "operator_profile": scenario.operator_profile,
            "marketplace_item": {
                "clause_id": clause.clause_id,
                "title": clause.title,
                "text": clause.text,
                "category": clause.category,
            },
            "required_output_schema": {
                "summary": "string",
                "recommendation": "string",
                "risk_level": "integer 1-10",
                "requires_human": "boolean",
                "question": "string",
                "options": ["string"],
            },
        }
        response = self._chat_json(prompt)
        finding = ClauseFinding(
            clause_id=clause.clause_id,
            title=clause.title,
            category=clause.category,
            risk_level=int(response.get("risk_level", clause.risk_level)),
            summary=response.get("summary", clause.summary),
            recommendation=response.get("recommendation", clause.recommendation),
            requires_human=bool(response.get("requires_human", clause.requires_human)),
            question=response.get("question", clause.question),
            options=list(response.get("options", clause.options)),
            proposed_operations=[
                ProposedOperation(
                    kind="auto_accept_clause",
                    summary=f"Decide whether to approve marketplace item {clause.clause_id} automatically.",
                    metadata={
                        "clause_id": clause.clause_id,
                        "category": clause.category,
                        "risk_level": int(response.get("risk_level", clause.risk_level)),
                        "requires_human": bool(response.get("requires_human", clause.requires_human)),
                    },
                )
            ],
        )
        for unsafe_operation in clause.unsafe_operations:
            finding.proposed_operations.append(
                ProposedOperation(
                    kind=unsafe_operation,
                    summary=f"Optional unsafe operation requested for marketplace item {clause.clause_id}.",
                    metadata={"clause_id": clause.clause_id},
                )
            )
        return finding

    def synthesize_report(
        self, scenario: Scenario, run_state: RunState, checkpoint_map: dict[str, dict[str, str]]
    ) -> str:
        prompt = {
            "task": "Create a concise HaaS marketplace operations report.",
            "scenario_title": scenario.title,
            "objective": scenario.objective,
            "operator_profile": scenario.operator_profile,
            "findings": [finding.to_dict() for finding in run_state.findings],
            "checkpoint_responses": checkpoint_map,
            "requirements": [
                "Summarize major risks.",
                "List operator-approved HaaS ops actions.",
                "State clearly that external outreach and real payout remain approval-gated.",
            ],
        }
        response = self._chat_json(prompt)
        report = response.get("report")
        if not isinstance(report, str) or not report.strip():
            raise RuntimeError("NIM reasoner did not return a valid report string.")
        return report.strip()

    def _chat_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        content = self.chat_text(
            system_prompt=(
                "You are a HaaS marketplace operations planning model. "
                "Return valid JSON only and do not wrap it in markdown."
            ),
            user_payload=payload,
            temperature=0.1,
            max_tokens=None,
        )
        return _extract_json_object(content)

    def chat_text(
        self,
        system_prompt: str,
        user_payload: dict[str, Any] | str,
        temperature: float = 0.1,
        max_tokens: int | None = None,
    ) -> str:
        endpoint = f"{self.base_url}/chat/completions"
        body = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        json.dumps(user_payload, ensure_ascii=True)
                        if isinstance(user_payload, dict)
                        else str(user_payload)
                    ),
                },
            ],
            "temperature": temperature,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        req = request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60, context=_default_ssl_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except ssl.SSLCertVerificationError:
            data = _curl_json(
                method="POST",
                url=endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                body=body,
            )
        except error.URLError as exc:
            if _is_ssl_verification_error(exc):
                data = _curl_json(
                    method="POST",
                    url=endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    body=body,
                )
            else:
                raise RuntimeError(f"NIM request failed: {exc}") from exc
        except Exception:
            data = _curl_json(
                method="POST",
                url=endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                body=body,
            )

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Unexpected NIM response format.") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("NIM response content was empty.")
        return content.strip()


def probe_nim_connection(
    api_key: str,
    model_name: str = DEFAULT_NIM_MODEL,
    base_url: str = DEFAULT_NIM_BASE_URL,
) -> dict[str, str]:
    reasoner = NimNemotronReasoner(model_name=model_name, base_url=base_url, api_key=api_key)
    content = reasoner.chat_text(
        system_prompt="Reply with READY only.",
        user_payload="Connectivity check. Reply with READY only.",
        temperature=0.0,
        max_tokens=8,
    )
    return {
        "backend": "nim",
        "model_name": model_name,
        "base_url": reasoner.base_url,
        "probe_reply": content,
    }


def fetch_nim_models(api_key: str, base_url: str = DEFAULT_NIM_BASE_URL) -> list[str]:
    endpoint = f"{base_url.rstrip('/')}/models"
    req = request.Request(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=30, context=_default_ssl_context()) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except ssl.SSLCertVerificationError:
        payload = _curl_json(
            method="GET",
            url=endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
        )
    except error.URLError as exc:
        if _is_ssl_verification_error(exc):
            payload = _curl_json(
                method="GET",
                url=endpoint,
                headers={"Authorization": f"Bearer {api_key}"},
            )
        else:
            return recommended_nim_models()
    data = payload.get("data", [])
    dynamic_models = [
        item.get("id", "").strip()
        for item in data
        if isinstance(item, dict) and item.get("id")
    ]
    return _merge_model_lists(dynamic_models, recommended_nim_models())


def _extract_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(line for line in lines if not line.startswith("```")).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model output was not valid JSON: {text}") from exc


def build_reasoner(
    backend: str,
    model_name: str = DEFAULT_NIM_MODEL,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> BaseReasoner:
    if backend == "scripted_nemotron":
        return ScriptedNemotronReasoner(model_name=model_name)
    if backend == "nim":
        return NimNemotronReasoner(
            model_name=model_name,
            base_url=base_url or os.getenv("NIM_BASE_URL", DEFAULT_NIM_BASE_URL),
            api_key=api_key,
        )
    raise ValueError(f"Unsupported reasoner backend: {backend}")


def _merge_model_lists(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for model_name in group:
            normalized = model_name.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            merged.append(normalized)
    return merged


def _curl_json(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    command = ["curl", "--silent", "--show-error", "--fail", "-X", method, url]
    for key, value in headers.items():
        command.extend(["-H", f"{key}: {value}"])
    if body is not None:
        command.extend(["-d", json.dumps(body, ensure_ascii=True)])
    completed = _run_curl(command, allow_insecure_retry=True)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("NIM response was not valid JSON.") from exc


def _run_curl(command: list[str], allow_insecure_retry: bool) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("NIM SSL fallback requires the system curl command, but curl was not found.") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip() or "unknown curl error"
        if allow_insecure_retry and _stderr_looks_like_ssl_cert_error(stderr):
            insecure_command = command[:1] + ["-k"] + command[1:]
            try:
                return subprocess.run(
                    insecure_command,
                    text=True,
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError as insecure_exc:
                insecure_stderr = (insecure_exc.stderr or "").strip() or "unknown curl error"
                raise RuntimeError(
                    "NIM TLS verification failed in both Python and curl. "
                    f"Final curl error: {insecure_stderr}"
                ) from insecure_exc
        raise RuntimeError(f"NIM request failed via curl: {stderr}") from exc


def _is_ssl_verification_error(exc: error.URLError) -> bool:
    reason = getattr(exc, "reason", None)
    if isinstance(reason, ssl.SSLCertVerificationError):
        return True
    return "CERTIFICATE_VERIFY_FAILED" in str(exc) or "certificate verify failed" in str(exc).lower()


def _stderr_looks_like_ssl_cert_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return (
        "certificate verify failed" in lowered
        or "ssl certificate problem" in lowered
        or "unable to get local issuer certificate" in lowered
    )
