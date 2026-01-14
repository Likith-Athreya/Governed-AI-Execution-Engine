from typing import Any, Dict, Optional, TypedDict, List
from langgraph.graph import StateGraph, END
from agents.governance_agents import (
    GovernanceDecisionAgent,
    suggest_remediation
)
from agents.llm_wrapper import call_llm, DEFAULT_MODEL

class GovernanceState(TypedDict, total=False):
    simulation: Dict[str, Any]
    policy: Dict[str, Any]
    decision: Dict[str, Any]
    risk_score: int
    risk_reasons: List[str]
    remediation: Dict[str, Any]
    episodic_memory: List[Dict[str, Any]]
    final_status: Optional[str]

def governance_decision_node(state: GovernanceState) -> GovernanceState:
    simulation: Dict[str, Any] = state.get("simulation", {})
    policy: Dict[str, Any] = state.get("policy", {})
    agent = GovernanceDecisionAgent()
    decision = agent.decide(sandbox_result=simulation, policy=policy)

    state["decision"] = decision
    return state

def risk_assessment_node(state: GovernanceState) -> GovernanceState:
    simulation: Dict[str, Any] = state.get("simulation", {})
    policy: Dict[str, Any] = state.get("policy", {})
    episodic_memory: List[Dict[str, Any]] = state.get("episodic_memory", [])

    prompt = f"""Analyze this database query simulation and assign a risk score from 0-100.

Simulation Data:
- Query Type: {simulation.get('query_type', 'Unknown')}
- Tables Accessed: {simulation.get('tables_accessed', [])}
- Columns Accessed: {simulation.get('columns_accessed', [])}
- Column Classifications: {simulation.get('column_classification', {})}
- Rows Returned: {simulation.get('rows_returned', 0)}
- Execution Time: {simulation.get('execution_time_ms', 0)}ms

Policy Context:
- Deny PII: {policy.get('deny_pii', False)}
- Blocked Columns: {policy.get('blocked_columns', [])}
- Max Rows: {policy.get('max_rows')}

Historical Context:
{chr(10).join([f"- Previous query accessed {len(mem.get('simulation', {}).get('columns_accessed', []))} columns, returned {mem.get('simulation', {}).get('rows_returned', 0)} rows" for mem in episodic_memory[-3:]]) if episodic_memory else "No previous queries"}

Based on all this information, provide:
1. Risk Score (0-100): [number only]
2. Risk Reasons: [brief explanation]

Risk Guidelines:
- PII access: +40-60 points
- Large datasets (>1000 rows): +20-30 points
- Blocked column access: +30-50 points
- Historical patterns: adjust based on context
- Policy violations: +50+ points"""

    try:
        analysis = call_llm(
            prompt=prompt,
            system_prompt="You are a database security analyst. Provide objective risk assessments based on the provided data.",
            temperature=0.3
        )

        lines = analysis.strip().split('\n')
        risk_score = 0
        reasons = []

        for line in lines:
            line_lower = line.lower()
            if 'risk score' in line_lower and ':' in line:
                try:
                    score_part = line.split(':', 1)[1].strip()
                    import re
                    numbers = re.findall(r'\d+', score_part)
                    if numbers:
                        risk_score = int(numbers[0])
                        risk_score = max(0, min(100, risk_score))
                except:
                    pass
            elif 'reason' in line_lower and ':' in line:
                reason_text = line.split(':', 1)[1].strip()
                if reason_text and reason_text != '[brief explanation]':
                    reasons.append(reason_text)

        if not reasons:
            if risk_score > 50:
                reasons.append("High risk query detected")
            elif risk_score > 20:
                reasons.append("Moderate risk query detected")
            else:
                reasons.append("Low risk query - assessment completed")

        state["risk_score"] = risk_score
        state["risk_reasons"] = reasons

    except Exception as e:
        state["risk_score"] = 50
        state["risk_reasons"] = [f"Risk assessment failed: {str(e)}"]

    return state

def remediation_node(state: GovernanceState) -> GovernanceState:
    decision: Dict[str, Any] = state.get("decision", {})
    simulation: Dict[str, Any] = state.get("simulation", {})
    remediation = suggest_remediation(decision=decision, sandbox_result=simulation)
    state["remediation"] = remediation
    return state

class GovernanceOrchestrator:
    def __init__(self) -> None:
        graph = StateGraph(GovernanceState)

        graph.add_node("governance_decision", governance_decision_node)
        graph.add_node("risk_assessment", risk_assessment_node)
        graph.add_node("remediation", remediation_node)

        graph.set_entry_point("governance_decision")

        graph.add_edge("governance_decision", "risk_assessment")
        graph.add_edge("risk_assessment", "remediation")
        graph.add_edge("remediation", END)

        self.app = graph.compile()

    def run(self, sandbox_result: Dict[str, Any], policy: Dict[str, Any], episodic_memory: list = None) -> Dict[str, Any]:

        initial_state: GovernanceState = {
            "simulation": sandbox_result,
            "policy": policy,
            "episodic_memory": episodic_memory or [],
        }

        final_state = self.app.invoke(initial_state)

        risk_assessment = {
            "risk_score": final_state.get("risk_score", 50),
            "reasons": final_state.get("risk_reasons", ["Assessment completed"])
        }

        return {
            "decision": final_state.get("decision", {}),
            "risk": risk_assessment,
            "remediation": final_state.get("remediation", {}),
        }