#!/usr/bin/env python3
"""
NemoClaw Long Agent reference implementation.

This file intentionally uses only the Python standard library. It does not
access the network and does not scan arbitrary local files. Runtime state is
limited to .nemoclaw/state.json inside this project directory.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


APP_NAME = "haas-nemoclaw-long-agent"
STATE_DIR = Path(".nemoclaw")
STATE_FILE = STATE_DIR / "state.json"
STATE_BACKUP = STATE_DIR / "state.backup.json"
REPORT_FILE = Path("NEMOCLAW_RUN_REPORT.md")


SEED_SIGNALS: List[Dict[str, Any]] = [
    {
        "id": "sig-001",
        "source": "offline_public_signal",
        "text": "I need three people to describe whether dark chocolate and jalapeno taste good together.",
        "requester": "demo_author_sensory",
        "category_hint": "sensory",
    },
    {
        "id": "sig-002",
        "source": "offline_public_signal",
        "text": "Find this person's home address and phone number so we can confront them tonight.",
        "requester": "demo_author_unsafe",
        "category_hint": "social_help",
    },
    {
        "id": "sig-003",
        "source": "offline_public_signal",
        "text": "I have 200000 NTD. Tell me exactly which stock to buy tomorrow and guarantee profit.",
        "requester": "demo_author_finance",
        "category_hint": "investing_opinion",
    },
]


POLICIES: List[Dict[str, Any]] = [
    {
        "id": "P-OUTREACH-001",
        "name": "External outreach must remain draft-only",
        "severity": "medium",
        "action": "require_approval",
    },
    {
        "id": "P-PRIVACY-001",
        "name": "Reject doxxing, private contact details, stalking, or confrontation",
        "severity": "high",
        "action": "refuse",
        "patterns": [
            r"\bhome address\b",
            r"\bphone number\b",
            r"\bconfront\b",
            r"\bstalk\b",
            r"\bdoxx\b",
            r"\btonight\b.*\bconfront\b",
        ],
    },
    {
        "id": "P-FINANCE-001",
        "name": "No personalized financial advice or guaranteed returns",
        "severity": "high",
        "action": "rewrite",
        "patterns": [
            r"\bexactly which stock\b",
            r"\bguarantee profit\b",
            r"\bguaranteed return\b",
            r"\bbuy tomorrow\b",
        ],
    },
    {
        "id": "P-HOMEWORK-001",
        "name": "Homework help must become tutoring, not completion",
        "severity": "medium",
        "action": "rewrite",
        "patterns": [r"\bwrite my assignment\b", r"\btake my test\b", r"\bdo my homework\b"],
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(exist_ok=True)


def default_state() -> Dict[str, Any]:
    now = utc_now()
    return {
        "app": APP_NAME,
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "model": {
            "provider": "NVIDIA",
            "name": "Nemotron",
            "adapter": "NemotronOfflineReasoner",
            "mode": "offline-deterministic",
        },
        "task": {
            "goal": "Turn offline public help signals into safe, verifiable HaaS tasks with durable progress.",
            "cursor": 0,
            "completed": False,
        },
        "signals": [
            {
                **signal,
                "state": "new",
                "risk_level": "unknown",
                "policy_hits": [],
                "quest": None,
                "submission": None,
                "reward": None,
            }
            for signal in SEED_SIGNALS
        ],
        "audit": [],
    }


def atomic_save(state: Dict[str, Any]) -> None:
    ensure_state_dir()
    state["updated_at"] = utc_now()
    temp_file = STATE_DIR / "state.tmp"
    temp_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if STATE_FILE.exists():
        shutil.copyfile(STATE_FILE, STATE_BACKUP)
    temp_file.replace(STATE_FILE)
    write_report(state)


def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        state = default_state()
        atomic_save(state)
        return state
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def audit(
    state: Dict[str, Any],
    action: str,
    target_id: str,
    input_summary: str,
    output_summary: str,
    risk_level: str,
    approval_required: str,
) -> None:
    state["audit"].append(
        {
            "timestamp": utc_now(),
            "actor": "nemoclaw",
            "agent": APP_NAME,
            "model": "Nemotron",
            "action": action,
            "target_type": "signal",
            "target_id": target_id,
            "input_summary": input_summary[:180],
            "output_summary": output_summary[:220],
            "risk_level": risk_level,
            "approval_required": approval_required,
        }
    )


class PolicyEngine:
    def evaluate(self, text: str) -> Tuple[str, str, List[Dict[str, str]]]:
        hits: List[Dict[str, str]] = []
        for policy in POLICIES:
            for pattern in policy.get("patterns", []):
                if re.search(pattern, text, flags=re.IGNORECASE):
                    hits.append(
                        {
                            "policy_id": policy["id"],
                            "name": policy["name"],
                            "severity": policy["severity"],
                            "action": policy["action"],
                        }
                    )
                    break

        if any(hit["action"] == "refuse" for hit in hits):
            return "high", "refuse", hits
        if any(hit["severity"] == "high" for hit in hits):
            return "high", "rewrite", hits
        if any(hit["severity"] == "medium" for hit in hits):
            return "medium", "rewrite", hits
        return "low", "allow", hits


class NemotronOfflineReasoner:
    """Deterministic adapter that exposes where Nemotron reasoning is used."""

    def make_quest(self, signal: Dict[str, Any], policy_action: str) -> Dict[str, Any]:
        text = signal["text"]
        if policy_action == "rewrite":
            if "stock" in text.lower() or "profit" in text.lower():
                title = "Collect general market risk perspectives"
                description = (
                    "Ask contributors for educational, non-personalized market risk perspectives. "
                    "Submissions must avoid buy/sell instructions and guaranteed returns."
                )
                category = "investing_opinion"
                rubric = [
                    "States that the response is general education, not personal advice",
                    "Mentions risks and uncertainty",
                    "Avoids exact buy/sell instructions",
                ]
            else:
                title = "Convert unsafe request into safe learning support"
                description = "Provide hints, explanations, and concept checks without completing prohibited work."
                category = "homework"
                rubric = ["Provides teaching steps", "Avoids completing the assignment", "Includes a practice check"]
        else:
            title = "Taste contrast notes for dark chocolate and jalapeno"
            description = (
                "Collect three concise sensory descriptions comparing bitterness, heat, sweetness, "
                "aftertaste, and whether the pairing feels pleasant."
            )
            category = signal.get("category_hint", "sensory")
            rubric = [
                "Mentions at least three sensory dimensions",
                "Explains whether the pairing works and why",
                "Keeps the answer subjective and experience-based",
            ]

        return {
            "title": title,
            "description": description,
            "category": category,
            "difficulty": "C" if category == "sensory" else "B",
            "reward_suggestion": {"asset": "XP", "amount": 45 if category == "sensory" else 30},
            "verification_rubric": rubric,
            "invite_draft": "Draft only: invite the requester to confirm and publish this task inside HaaS.",
            "reasoning_model": "Nemotron",
        }

    def verify_submission(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        quest = signal["quest"]
        return {
            "submission_id": f"sub-{signal['id'][-3:]}",
            "summary": f"Offline demo submission satisfies {len(quest['verification_rubric'])} rubric items.",
            "verdict": "accepted",
            "checked_by": "NemotronOfflineReasoner",
        }


class LongAgent:
    def __init__(self, state: Dict[str, Any]) -> None:
        self.state = state
        self.policy = PolicyEngine()
        self.reasoner = NemotronOfflineReasoner()

    def next_signal(self) -> Optional[Dict[str, Any]]:
        for signal in self.state["signals"]:
            if signal["state"] != "done" and signal["state"] != "blocked":
                return signal
        return None

    def step(self) -> str:
        signal = self.next_signal()
        if signal is None:
            if self.state["task"]["completed"]:
                return "COMPLETE already completed"
            self.state["task"]["completed"] = True
            audit(
                self.state,
                "task.complete",
                "all",
                "All offline signals processed",
                "Long task completed without network access or arbitrary local-file reads",
                "low",
                "none",
            )
            return "COMPLETE all signals processed"

        text = signal["text"]
        if signal["state"] == "new":
            signal["state"] = "scouted"
            audit(self.state, "scout.capture", signal["id"], text, "Captured bundled offline signal", "low", "none")
            return f"SCOUTED {signal['id']}"

        if signal["state"] == "scouted":
            risk, action, hits = self.policy.evaluate(text)
            signal["risk_level"] = risk
            signal["policy_action"] = action
            signal["policy_hits"] = hits
            signal["state"] = "policy_reviewed"
            audit(
                self.state,
                "policy.evaluate",
                signal["id"],
                text,
                f"risk={risk}, action={action}, hits={len(hits)}",
                risk,
                "external outreach and payout remain approval gated",
            )
            return f"POLICY {signal['id']} risk={risk} action={action}"

        if signal["state"] == "policy_reviewed":
            if signal.get("policy_action") == "refuse":
                signal["state"] = "blocked"
                signal["quest"] = None
                audit(
                    self.state,
                    "guardrail.refuse",
                    signal["id"],
                    text,
                    "Refused unsafe request and did not create a task",
                    signal["risk_level"],
                    "human review required for any appeal",
                )
                return f"REFUSED {signal['id']} policy={signal['policy_hits'][0]['policy_id']}"

            signal["quest"] = self.reasoner.make_quest(signal, signal.get("policy_action", "allow"))
            signal["state"] = "drafted"
            audit(
                self.state,
                "quest.draft",
                signal["id"],
                text,
                signal["quest"]["title"],
                signal["risk_level"],
                "requester approval required before publication",
            )
            return f"DRAFTED {signal['id']} title={signal['quest']['title']}"

        if signal["state"] == "drafted":
            signal["submission"] = self.reasoner.verify_submission(signal)
            signal["state"] = "verified"
            audit(
                self.state,
                "verifier.accept",
                signal["id"],
                signal["quest"]["title"],
                signal["submission"]["summary"],
                signal["risk_level"],
                "payout proposal only",
            )
            return f"VERIFIED {signal['id']} verdict=accepted"

        if signal["state"] == "verified":
            amount = signal["quest"]["reward_suggestion"]["amount"]
            signal["reward"] = {"asset": "XP", "amount": amount, "status": "proposal_only"}
            signal["state"] = "done"
            audit(
                self.state,
                "reward.propose",
                signal["id"],
                signal["submission"]["submission_id"],
                f"Proposed {amount} XP; no real funds moved",
                signal["risk_level"],
                "human/accounting approval required for real payout",
            )
            return f"REWARD_PROPOSED {signal['id']} {amount} XP"

        raise RuntimeError(f"Unknown state for {signal['id']}: {signal['state']}")


def summarize(state: Dict[str, Any]) -> str:
    counts: Dict[str, int] = {}
    for signal in state["signals"]:
        counts[signal["state"]] = counts.get(signal["state"], 0) + 1
    high_risk = [s["id"] for s in state["signals"] if s["risk_level"] == "high"]
    return "\n".join(
        [
            "HaaS NemoClaw Long Agent Status",
            f"- model: {state['model']['name']} via {state['model']['adapter']} ({state['model']['mode']})",
            f"- state_file: {STATE_FILE}",
            f"- completed: {state['task']['completed']}",
            f"- states: {counts}",
            f"- high_risk: {high_risk}",
            f"- audit_events: {len(state['audit'])}",
        ]
    )


def write_report(state: Dict[str, Any]) -> None:
    lines = [
        "# NemoClaw Run Report",
        "",
        "This file is generated by `python3 main.py` so NemoClaw/OpenClaw can inspect the result without reading terminal history.",
        "",
        "## Status",
        "",
        f"- App: `{state['app']}`",
        f"- Updated at: `{state['updated_at']}`",
        f"- Model: `{state['model']['name']}` via `{state['model']['adapter']}`",
        f"- Mode: `{state['model']['mode']}`",
        f"- Completed: `{state['task']['completed']}`",
        f"- Audit events: `{len(state['audit'])}`",
        "",
        "## Signals",
        "",
    ]
    for signal in state["signals"]:
        lines.extend(
            [
                f"### {signal['id']}",
                "",
                f"- State: `{signal['state']}`",
                f"- Risk: `{signal['risk_level']}`",
                f"- Policy action: `{signal.get('policy_action', 'pending')}`",
                f"- Source text: {signal['text']}",
            ]
        )
        if signal.get("policy_hits"):
            policies = ", ".join(hit["policy_id"] for hit in signal["policy_hits"])
            lines.append(f"- Policy hits: `{policies}`")
        if signal.get("quest"):
            lines.append(f"- Quest: {signal['quest']['title']}")
        if signal.get("reward"):
            reward = signal["reward"]
            lines.append(f"- Reward: `{reward['amount']} {reward['asset']} ({reward['status']})`")
        lines.append("")

    lines.extend(["## Latest Audit Events", ""])
    for event in state["audit"][-8:]:
        lines.append(
            f"- `{event['timestamp']}` `{event['action']}` `{event['target_id']}` "
            f"risk=`{event['risk_level']}`: {event['output_summary']}"
        )
    lines.append("")
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def run_steps(max_steps: Optional[int]) -> None:
    state = load_state()
    agent = LongAgent(state)
    steps = 0
    while max_steps is None or steps < max_steps:
        result = agent.step()
        atomic_save(state)
        print(result)
        steps += 1
        if result.startswith("COMPLETE"):
            break
    print()
    print(summarize(state))


def reset_state() -> None:
    ensure_state_dir()
    state = default_state()
    atomic_save(state)
    print(f"Reset complete: {STATE_FILE}")


def policy_test() -> None:
    samples = [
        "Describe the taste of chocolate and jalapeno.",
        "Find their home address and phone number so we can confront them.",
        "Tell me exactly which stock to buy tomorrow and guarantee profit.",
        "Write my assignment for me.",
    ]
    engine = PolicyEngine()
    for sample in samples:
        risk, action, hits = engine.evaluate(sample)
        policies = ",".join(hit["policy_id"] for hit in hits) or "none"
        print(f"{action.upper():7} risk={risk:6} policies={policies} :: {sample}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline NemoClaw Long Agent for HaaS")
    parser.add_argument(
        "--mode",
        choices=["demo", "run", "resume", "step", "status", "reset", "policy-test"],
        default="demo",
        help="demo/run process the durable task; resume is an alias for run; step advances once.",
    )
    parser.add_argument("--max-steps", type=int, default=None, help="Stop after N durable operations.")
    args = parser.parse_args()

    if args.mode == "reset":
        reset_state()
    elif args.mode == "status":
        print(summarize(load_state()))
    elif args.mode == "policy-test":
        policy_test()
    elif args.mode == "step":
        run_steps(1)
    elif args.mode in {"demo", "run", "resume"}:
        run_steps(args.max_steps)


if __name__ == "__main__":
    main()
