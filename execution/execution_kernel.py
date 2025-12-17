from core.sandbox.sandbox_manager import SandboxManager
from agentic.governance_orchestrator import GovernanceOrchestrator
from core.sandbox.utils import execute_query
from catalog.pii_classifier import PIIClassifier
import re

class ExecutionKernel:
    def __init__(self, policy: dict):
        self.policy = policy
        self.governance_orchestrator = GovernanceOrchestrator()
        self.pii_classifier = PIIClassifier()

    def extract_columns(self, sql: str)-> list:
        match = re.search(r"select\s+(.*?)\s+from", sql, re.IGNORECASE)
        if not match:
            return []
        return [c.strip() for c in match.group(1).split(",")]

    def run_sql(self, sql: dict)-> dict:
        sandbox = SandboxManager()
        sandbox_result = sandbox.simulate_query(sql)

        columns = self.extract_columns(sql)
        column_classes = self.pii_classifier.classify_columns(columns)
        pii_columns = [
            col for col, cls in column_classes.items() if cls == "PII"
        ]

        if pii_columns:
            return {
                "status": "DENIED",
                "sql": sql,
                "reason": f"PII access detected: {pii_columns}"
            }

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

