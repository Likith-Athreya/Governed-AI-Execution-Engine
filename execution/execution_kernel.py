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

    def extract_columns(self, sql: str) -> list:
        match = re.search(r"select\s+(.*?)\s+from", sql, re.IGNORECASE)
        if not match:
            return []
        return [c.strip() for c in match.group(1).split(",")]

    def run_sql(self, sql: str, simulation: dict) -> dict:
        # Hard block if simulation already failed
        if not simulation.get("valid", False):
            return {
                "status": "DENIED",
                "reason": "Simulation invalid",
                "simulation": simulation
            }

        # Governance orchestration
        governance_result = self.governance_orchestrator.run(
            sandbox_result=simulation,
            policy=self.policy
        )

        decision = governance_result["decision"]["decision"]
        if decision == "DENY":
            return {
                "status": "DENIED",
                "sql": sql,
                "governance": governance_result,
                "simulation": simulation
            }

        # Execute real query (SQLite)
        query_result = execute_query(sql)
        rows = query_result.get("rows", [])

        # Build tabular response
        columns = simulation.get("columns_accessed", [])
        data = {
            "columns": columns,
            "rows": rows
        }

        return {
            "status": "ALLOWED",
            "sql": sql,
            "simulation": simulation,
            "governance": governance_result,
            "data": data,
            "message": "query approved after simulation"
        }
