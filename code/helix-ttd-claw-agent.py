"""
Helix-TTD-Claw Agent: Runnable Entry Point

Imports all classes from openclaw_agent (canonical importable module)
and runs usage examples. Run directly with: python helix-ttd-claw-agent.py
"""

from openclaw_agent import (
    AgencyLevel,
    AgentAction,
    AgentPlan,
    ConstitutionalCheckpoint,
    EpistemicLabel,
    HelixConstitutionalGate,
    OpenClawAgent,
    RiskConfiguration,
)

# ============================================================
# USAGE EXAMPLES
# ============================================================

def example_bounded_agent_workflow():
    """
    Example: A bounded agent that analyzes code with full constitutional checkpoints.
    """
    agent = OpenClawAgent(agency_tier=AgencyLevel.BOUNDED_TOOLS)

    def noop(x):
        return x
    agent.register_tool("file_search", noop, risk_level=0.2)
    agent.register_tool("file_read", noop, risk_level=0.1)
    agent.register_tool("static_analysis", noop, risk_level=0.3)

    plan = agent.create_plan(
        objective="Analyze Python codebase for potential improvements",
        context={"directory": "./src"}
    )

    print(f"[PLAN CREATED] {plan.plan_id}")
    print(f"  Objective: {plan.objective}")
    print(f"  Steps: {len(plan.steps)}")

    results = agent.execute_with_checkpoints(plan)

    print(f"\n[EXECUTION RESULTS]")
    print(f"  Status: {results['status']}")
    print(f"  Checkpoints: {len(results['checkpoints'])}")
    for cp in results['checkpoints']:
        print(f"    - {cp['id']}: {cp['compliance']*100:.0f}% compliance")
        if cp['drift']:
            print(f"      DRIFT: {cp['codes']}")

    print(f"  Merkle Root: {results['final_anchor']}")

    return results


def example_high_risk_gate():
    """
    Example: High-risk action requiring custodian approval.
    Demonstrates the CUSTODIAN_GATE tier.
    """
    agent = OpenClawAgent(agency_tier=AgencyLevel.CUSTODIAN_GATE)

    def noop(x):
        return x
    agent.register_tool("database_migrate", noop, risk_level=0.9)

    risky_plan = AgentPlan(
        plan_id="risky_001",
        objective="Update production database schema",
        steps=[
            AgentAction(
                action_id="db_1",
                action_type="execute",
                tool_name="database_migrate",
                parameters={"operation": "ALTER TABLE..."},
                rationale="[ASSUMPTION] Schema migration is required for new feature",
                epistemic_basis=EpistemicLabel.ASSUMPTION,
                estimated_risk=0.9
            )
        ],
        assumptions=["Backup completed", "Migration tested in staging"],
        estimated_completion=10.0
    )

    results_no_approval = agent.execute_with_checkpoints(risky_plan, custodian_approval=None)
    if results_no_approval['executions']:
        print(f"[WITHOUT APPROVAL] {results_no_approval['executions'][0]['status']}")
    else:
        print(f"[WITHOUT APPROVAL] Plan blocked: {results_no_approval.get('reason', 'No reason')}")

    risky_plan2 = AgentPlan(
        plan_id="risky_002",
        objective="Update production database schema",
        steps=[
            AgentAction(
                action_id="db_1",
                action_type="execute",
                tool_name="database_migrate",
                parameters={"operation": "ALTER TABLE..."},
                rationale="[ASSUMPTION] Schema migration is required for new feature",
                epistemic_basis=EpistemicLabel.ASSUMPTION,
                estimated_risk=0.9
            )
        ],
        assumptions=["Backup completed"],
        estimated_completion=10.0
    )
    results_approved = agent.execute_with_checkpoints(risky_plan2, custodian_approval=True)
    if results_approved['executions']:
        print(f"[WITH APPROVAL] {results_approved['executions'][0]['status']}")
    else:
        print(f"[WITH APPROVAL] {results_approved['status']}")


def example_drift_detection():
    """
    Example: Agent attempts self-modification (constitutional violation).
    """
    agent = OpenClawAgent(agency_tier=AgencyLevel.BOUNDED_TOOLS)

    bad_plan = AgentPlan(
        plan_id="bad_001",
        objective="Improve agent performance",
        steps=[
            AgentAction(
                action_id="mod_1",
                action_type="modify",
                tool_name="self_update_agent",
                parameters={"new_behavior": "autonomous"},
                rationale="Self-improvement will optimize outcomes",
                epistemic_basis=EpistemicLabel.HYPOTHESIS,
                estimated_risk=1.0
            )
        ],
        assumptions=["Self-modification is safe"],
        estimated_completion=1.0
    )

    results = agent.execute_with_checkpoints(bad_plan)
    print(f"[DRIFT DETECTED] {results['status']}")
    print(f"  Violations: {results.get('reason', 'N/A')}")


def example_granular_risk_tuning():
    """
    Example: Demonstrating incremental risk levers.
    Same high-risk action, different configurations.
    """
    print("\n[GRANULAR RISK TUNING DEMO]")

    conservative_risk = RiskConfiguration(
        planning_max_risk=0.6,
        action_max_risk=0.7,
        override_max_risk=0.9,
        daily_risk_budget=5.0,
        tool_multipliers={"database_migrate": 1.5, "file_delete": 2.0}
    )

    permissive_risk = RiskConfiguration(
        planning_max_risk=0.85,
        action_max_risk=0.95,
        override_max_risk=0.99,
        daily_risk_budget=20.0,
        custodian_can_override=True,
        tool_multipliers={"database_migrate": 1.0, "file_delete": 1.2}
    )

    production_risk = RiskConfiguration(
        planning_max_risk=0.5,
        action_max_risk=0.6,
        override_max_risk=0.8,
        daily_risk_budget=3.0,
        custodian_can_override=False,
        tool_multipliers={"database_migrate": 2.0, "file_delete": 3.0}
    )

    configs = [
        ("Conservative", conservative_risk),
        ("Permissive", permissive_risk),
        ("Production", production_risk)
    ]

    for name, risk_config in configs:
        agent = OpenClawAgent(
            agency_tier=AgencyLevel.CUSTODIAN_GATE,
            risk_config=risk_config
        )
        def noop(x):
            return x
        agent.register_tool("database_migrate", noop, risk_level=0.8)

        plan = AgentPlan(
            plan_id=f"risk_test_{name.lower()}",
            objective=f"Test with {name} config",
            steps=[
                AgentAction(
                    action_id="db_1",
                    action_type="execute",
                    tool_name="database_migrate",
                    parameters={"operation": "ALTER TABLE..."},
                    rationale="[ASSUMPTION] Migration is safe",
                    epistemic_basis=EpistemicLabel.ASSUMPTION,
                    estimated_risk=0.8
                )
            ],
            assumptions=[],
            estimated_completion=5.0
        )

        effective = risk_config.calculate_effective_risk(0.8, "database_migrate")
        velocity = risk_config.get_risk_velocity()

        results = agent.execute_with_checkpoints(plan, custodian_approval=True)

        print(f"\n  {name} Config:")
        print(f"    Base Risk: 0.8 -> Effective: {effective:.2f}")
        print(f"    Action Max: {risk_config.action_max_risk}, Override Max: {risk_config.override_max_risk}")
        print(f"    Daily Budget: {velocity['budget']:.1f}, Can Override: {risk_config.custodian_can_override}")
        print(f"    Result: {results['status']}")


if __name__ == "__main__":
    print("=" * 60)
    print("Helix-TTD-Claw Agent with Constitutional Checkpoints")
    print("=" * 60)

    print("\n[EXAMPLE 1: Bounded Workflow]")
    example_bounded_agent_workflow()

    print("\n[EXAMPLE 2: High-Risk Gate]")
    example_high_risk_gate()

    print("\n[EXAMPLE 3: Drift Detection]")
    example_drift_detection()

    print("\n[EXAMPLE 4: Granular Risk Tuning]")
    example_granular_risk_tuning()

    print("\n" + "=" * 60)
    print("All examples completed. Constitutional integrity maintained.")
    print("=" * 60)
