import re
from core.sandbox.utils import execute_query
from catalog.pii_classifier import PIIClassifier
from core.audit_logger import log_audit
from agentic.governance_orchestrator import GovernanceOrchestrator


class ExecutionKernel:
    """
    The single source of truth for governed execution.
    NOTHING executes without passing through this kernel.
    """

    def __init__(self, policy: dict):
        self.policy = policy
        self.governance_orchestrator = GovernanceOrchestrator()
        self.pii_classifier = PIIClassifier()

    def extract_columns(self, sql: str) -> list:
        """
        Extract columns from a SELECT query for additional safety checks.
        """
        match = re.search(r"select\s+(.*?)\s+from", sql, re.IGNORECASE)
        if not match:
            return []
        return [c.strip() for c in match.group(1).split(",")]

    def run_sql(self, sql: str, simulation: dict) -> dict:
        """
        Execute SQL ONLY if simulation + governance approve it.
        """

        if not simulation.get("valid", False):
            log_audit(
                user_input=None,
                sql=sql,
                decision="DENIED",
                reason="Simulation invalid",
                simulation=simulation
            )
            return {
                "status": "DENIED",
                "reason": "Simulation invalid",
                "simulation": simulation
            }

        max_rows = self.policy.get("max_rows")
        if max_rows and simulation.get("rows_returned", 0) > max_rows:
            reason = f"Row limit exceeded: {simulation['rows_returned']} > {max_rows}"
            log_audit(
                user_input=None,
                sql=sql,
                decision="DENIED",
                reason=reason,
                simulation=simulation
            )
            return {
                "status": "DENIED",
                "reason": reason,
                "simulation": simulation
            }

        if self.policy.get("deny_pii", False):
            pii_columns = [
                col for col, cls in simulation.get("column_classification", {}).items()
                if cls == "PII"
            ]
            if pii_columns:
                reason = f"PII access denied: {pii_columns}"
                log_audit(
                    user_input=None,
                    sql=sql,
                    decision="DENIED",
                    reason=reason,
                    simulation=simulation
                )
                return {
                    "status": "DENIED",
                    "reason": reason,
                    "simulation": simulation
                }

        governance_result = self.governance_orchestrator.run(
            sandbox_result=simulation,
            policy=self.policy
        )

        decision = governance_result.get("decision", {}).get("decision")

        if decision == "DENY":
            reason = governance_result["decision"].get("explanation", "Governance denied execution")
            log_audit(
                user_input=None,
                sql=sql,
                decision="DENIED",
                reason=reason,
                simulation=simulation
            )
            return {
                "status": "DENIED",
                "sql": sql,
                "simulation": simulation,
                "governance": governance_result
            }

        query_result = execute_query(sql)

        rows = query_result.get("rows", [])
        columns = query_result.get("columns", simulation.get("columns_accessed", []))

        data = {
            "columns": columns,
            "rows": rows
        }

        log_audit(
            user_input=None,
            sql=sql,
            decision="ALLOWED",
            reason="Passed simulation and governance",
            simulation=simulation
        )

        return {
            "status": "ALLOWED",
            "sql": sql,
            "simulation": simulation,
            "governance": governance_result,
            "data": data,
            "message": "Query approved after simulation"
        }
