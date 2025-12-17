from agents.governance_decision_agent import GovernanceDecisionAgent
from agents.risk_agent import RiskAssessmentAgent
from agents.remediation_agent import RemediationAgent

class GovernanceOrchestrator:
    def __init__(self):
        self.decision_agent = GovernanceDecisionAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.remediation_agent = RemediationAgent()
    
    def run(self, sandbox_result: dict, policy: dict)-> dict:
        state = {}
        decision = self.decision_agent.decide(sandbox_result, policy)
        state['decision'] = decision

        risk = self.risk_agent.assess(sandbox_result)
        state['risk'] = risk

        remediation = self.remediation_agent.suggest(decision, sandbox_result)
        state['remediation'] = remediation

        return state