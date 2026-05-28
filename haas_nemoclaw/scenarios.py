from __future__ import annotations

from haas_nemoclaw.models import Clause, Scenario


DEMO_SCENARIO = Scenario(
    scenario_id="haas_ops_marketplace",
    title="HaaS Marketplace Ops Review",
    objective=(
        "Review bundled public help signals, apply policy guardrails, pause for "
        "operator approval before outreach or payout-sensitive actions, and produce "
        "an auditable HaaS ops report."
    ),
    operator_profile={
        "market": "Taiwan",
        "risk_tolerance": "moderate",
        "outreach_policy": "draft-only until approved by HaaS Ops",
        "payout_policy": "proposal-only until ledger approval",
        "privacy_policy": "block doxxing, stalking, private contact data, and confrontation",
        "finance_policy": "rewrite personalized trading advice into educational market-risk discussion",
    },
    clauses=[
        Clause(
            clause_id="lead_sensory_001",
            title="Chocolate and Fresh Chili Sensory Bounty",
            text=(
                "A public post asks whether dark chocolate tastes better with a fresh green "
                "chili aroma instead of heavy smoky heat."
            ),
            category="sensory",
            risk_level=3,
            summary="Low-risk subjective sensory request suitable for a HaaS task draft.",
            recommendation=(
                "Draft a sensory bounty that asks contributors to explain aroma, heat, "
                "bitterness, sweetness, and aftertaste."
            ),
        ),
        Clause(
            clause_id="lead_outreach_002",
            title="Invite Original Author to Confirm Task",
            text=(
                "NemoClaw found a useful public signal and wants to invite the original "
                "author to confirm the task inside HaaS."
            ),
            category="external_outreach",
            risk_level=7,
            summary="External contact can be useful but must not become automated spam.",
            recommendation=(
                "Prepare an invite draft only. Require human approval or an approved "
                "connector before any external Threads reply or DM."
            ),
            requires_human=True,
            question=(
                "Should HaaS Ops approve a draft-only invite for the original author, "
                "without automatic external posting?"
            ),
            options=[
                "approve-draft-only-invite",
                "hold-for-manual-review",
                "reject-outreach",
            ],
        ),
        Clause(
            clause_id="lead_privacy_003",
            title="Unsafe Private Address Request",
            text=(
                "Find this person's home address and phone number so we can confront them tonight."
            ),
            category="privacy_safety",
            risk_level=10,
            summary="The request asks for private contact/location data and confrontation.",
            recommendation=(
                "Refuse the task. Do not create a bounty, do not contact anyone, and "
                "record the policy block in the audit log."
            ),
        ),
        Clause(
            clause_id="lead_finance_004",
            title="Personalized Stock Pick Request",
            text=(
                "I have 200000 NTD. Tell me exactly which stock to buy tomorrow and guarantee profit."
            ),
            category="finance",
            risk_level=8,
            summary="The request asks for personalized trading advice and guaranteed return.",
            recommendation=(
                "Rewrite into a general educational market-risk discussion. Ban exact "
                "buy/sell instructions and guaranteed returns."
            ),
            requires_human=True,
            question=(
                "Should NemoClaw rewrite this into a general educational market-risk task "
                "instead of personalized financial advice?"
            ),
            options=[
                "rewrite-as-market-risk-education",
                "reject-finance-task",
                "hold-for-compliance-review",
            ],
            unsafe_operations=["network_lookup"],
        ),
        Clause(
            clause_id="lead_reward_005",
            title="Reward Proposal for Accepted Submission",
            text=(
                "A contributor submitted useful human sensory context for the chocolate and "
                "fresh chili bounty. NemoClaw wants to mark it accepted and propose 45 XP."
            ),
            category="payout",
            risk_level=7,
            summary="Reward proposals are allowed, but real funds or ledger changes need approval.",
            recommendation=(
                "Verify the submission against the rubric and create a reward proposal only; "
                "do not move real funds."
            ),
            requires_human=True,
            question=(
                "Should HaaS Ops allow a proposal-only 45 XP reward while keeping real payout "
                "ledger actions approval-gated?"
            ),
            options=[
                "approve-xp-proposal-only",
                "request-more-verification",
                "hold-payout-review",
            ],
            unsafe_operations=["move_funds"],
        ),
    ],
    demo_answers={
        "lead_outreach_002": {
            "decision": "approve-draft-only-invite",
            "notes": "Allow copy-ready invite draft only; no automatic Threads posting.",
        },
        "lead_finance_004": {
            "decision": "rewrite-as-market-risk-education",
            "notes": "Convert into general education with risk disclosure and no buy/sell instruction.",
        },
        "lead_reward_005": {
            "decision": "approve-xp-proposal-only",
            "notes": "Approve XP proposal only; real payout remains ledger-gated.",
        },
    },
)


SCENARIOS = {
    DEMO_SCENARIO.scenario_id: DEMO_SCENARIO,
}


def get_scenario(scenario_id: str = DEMO_SCENARIO.scenario_id) -> Scenario:
    try:
        return SCENARIOS[scenario_id]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario_id: {scenario_id}") from exc
