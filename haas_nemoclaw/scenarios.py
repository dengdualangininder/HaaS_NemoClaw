from __future__ import annotations

from haas_nemoclaw.models import Clause, Scenario


DEMO_SCENARIO = Scenario(
    scenario_id="saas_vendor_msa",
    title="SaaS Vendor Contract Review",
    objective=(
        "Review a vendor MSA, flag risky clauses, pause for business judgment "
        "when policy requires human approval, and output a negotiation plan."
    ),
    operator_profile={
        "jurisdiction": "Taiwan",
        "risk_tolerance": "moderate",
        "preferred_liability_cap": "12 months of fees",
        "required_cure_period_days": 30,
        "cross_border_data_transfer": "requires DPA and subprocessor notice",
    },
    clauses=[
        Clause(
            clause_id="liability_7_3",
            title="Unlimited Liability",
            text=(
                "Supplier shall have unlimited liability for all direct and indirect losses "
                "arising from service delivery."
            ),
            category="liability",
            risk_level=9,
            summary="The clause exposes the buyer to open-ended financial risk.",
            recommendation=(
                "Do not accept as drafted. Add a total liability cap tied to contract value."
            ),
            requires_human=True,
            question=(
                "Should the agent reject unlimited liability and request a cap based on the "
                "operator playbook?"
            ),
            options=[
                "request-liability-cap",
                "accept-as-is",
                "escalate-to-counsel",
            ],
        ),
        Clause(
            clause_id="privacy_4_1",
            title="Cross-Border Data Transfers",
            text=(
                "Vendor may transfer customer usage data to any affiliate or processor "
                "worldwide without prior notice."
            ),
            category="privacy",
            risk_level=8,
            summary="The clause weakens operator control over international data transfer.",
            recommendation=(
                "Require DPA language, subprocessor notice, and approval for material transfer changes."
            ),
            requires_human=True,
            question=(
                "Should the agent require a DPA and subprocessor notification clause before acceptance?"
            ),
            options=[
                "require-dpa-and-notice",
                "accept-transfer-language",
                "escalate-to-counsel",
            ],
            unsafe_operations=["network_lookup"],
        ),
        Clause(
            clause_id="termination_11_2",
            title="Convenience Termination",
            text=(
                "Vendor may terminate the service for convenience on seven days' notice "
                "without a cure period."
            ),
            category="termination",
            risk_level=7,
            summary="The clause creates continuity risk if the vendor can exit quickly.",
            recommendation=(
                "Add a cure period and longer notice before convenience termination becomes effective."
            ),
            requires_human=True,
            question=(
                "Should the agent insist on a 30-day cure period and extended notice before termination?"
            ),
            options=[
                "require-30-day-cure",
                "accept-7-day-termination",
                "escalate-to-counsel",
            ],
            unsafe_operations=["read_host_file"],
        ),
        Clause(
            clause_id="pricing_2_1",
            title="Annual Pricing Adjustment",
            text=(
                "Annual price increases are limited to CPI-linked adjustments once per year."
            ),
            category="pricing",
            risk_level=3,
            summary="The pricing clause is bounded and commercially normal.",
            recommendation="Accept as drafted.",
        ),
    ],
    demo_answers={
        "liability_7_3": {
            "decision": "request-liability-cap",
            "notes": "Cap total liability at 12 months of fees.",
        },
        "privacy_4_1": {
            "decision": "require-dpa-and-notice",
            "notes": "Require subprocessor notice and DPA commitments.",
        },
        "termination_11_2": {
            "decision": "require-30-day-cure",
            "notes": "Maintain continuity with a cure period and longer notice.",
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
