from core.sandbox.sandbox_manager import SandboxManager
from agentic.governance_orchestrator import GovernanceOrchestrator
from core.sandbox.utils import execute_query

class ExecutionKernel:
    def __init__(self, policy: dict):
        self.policy = policy
        self.governance_orchestrator = GovernanceOrchestrator()

    def run_sql(self, sql: dict)-> dict:
        sandbox = SandboxManager()
        sandbox_result = sandbox.simulate_query(sql)

        governance_result = self.governance_orchestrator.run(
            sandbox_result = sandbox_result, policy = self.policy
        )

        decision = governance_result["decision"]["decision"]
        if decision =="DENY": 
            return{
                "status": "BLOCKED",
                "sql": sql,
                "governance": governance_result
            }
        data = execute_query(sql)
        
        return{
            "status":"ALLOWED",
            "sql":sql,
            "governance": governance_result,
            "message": "query approved for execution"
        }

