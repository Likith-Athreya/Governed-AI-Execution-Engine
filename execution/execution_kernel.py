import time
from core.sandbox.sandbox_manager import execute_query
from core.audit_logger import log_audit
from agentic.governance_orchestrator import GovernanceOrchestrator

class ExecutionKernel:

    def __init__(self, policy: dict):
        self.policy = policy
        self.governance_orchestrator = GovernanceOrchestrator()
        self.episodic_memory = []

    def _deny_execution(self, sql: str, simulation: dict, reason: str, governance_result: dict = None) -> dict:
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
            "governance": governance_result,
            "reason": reason
        }

    def run_sql(self, sql: str, simulation: dict) -> dict:
        if not simulation.get("valid", False):
            return self._deny_execution(sql, simulation, "Simulation invalid")

        self.episodic_memory.append({
            "sql": sql,
            "simulation": simulation,
            "timestamp": time.time()
        })
        if len(self.episodic_memory) > 10:
            self.episodic_memory = self.episodic_memory[-10:]

        governance_result = self.governance_orchestrator.run(
            sandbox_result=simulation,
            policy=self.policy,
            episodic_memory=self.episodic_memory
        )

        decision = governance_result.get("decision", {}).get("decision")
        if decision == "DENY":
            return self._deny_execution(sql, simulation, governance_result["decision"].get("explanation", "Governance denied execution"), governance_result)

        query_result = execute_query(sql)

        rows = query_result.get("rows", [])
        columns = query_result.get("columns", simulation.get("columns_accessed", []))

        max_rows = self.policy.get("max_rows")
        if max_rows and len(rows) > max_rows:
            rows = rows[:max_rows]

        if decision == "ALLOW_WITH_FILTERING":
            if simulation.get("query_type") == "UPDATE":
                log_audit(
                    user_input=None,
                    sql=sql,
                    decision="DENIED",
                    reason="UPDATE operations cannot be filtered",
                    simulation=simulation
                )
                return {
                    "status": "DENIED",
                    "sql": sql,
                    "simulation": simulation,
                    "governance": governance_result,
                    "message": "UPDATE operations cannot be filtered"
                }

            cols_to_filter = set(governance_result["decision"].get("columns_to_filter", []))
            if cols_to_filter and columns:
                keep_indices = [i for i, col in enumerate(columns) if col not in cols_to_filter]
                columns = [columns[i] for i in keep_indices]
                filtered_rows = []
                for row in rows:
                    filtered_row = [row[i] for i in keep_indices]
                    filtered_rows.append(filtered_row)
                rows = filtered_rows

        if simulation.get("query_type") == "UPDATE":
            update_result = execute_query(sql)
            affected_rows = update_result.get("affected_rows", 0)

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
                "data": {
                    "operation": "UPDATE",
                    "rows_affected": affected_rows
                },
                "message": f"UPDATE operation completed successfully. {affected_rows} rows affected."
            }

        else:
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