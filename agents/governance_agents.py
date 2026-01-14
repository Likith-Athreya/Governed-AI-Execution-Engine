class GovernanceDecisionAgent:
    def decide(self, sandbox_result: dict, policy: dict) -> dict:
        query_type = sandbox_result.get("query_type", "SELECT")
        classifications = sandbox_result.get("column_classification", {})
        accessed_types = set(classifications.values())
        accessed_columns = set(sandbox_result.get("columns_accessed", []))
        explanation = []

        pii_accessed = "PII" in accessed_types

        if query_type == "UPDATE":
            explanation.append("UPDATE operation detected.")

            if pii_accessed:
                explanation.append("UPDATE operation involves PII data.")
                if policy.get("deny_pii_access", False) or policy.get("deny_pii", False):
                    explanation.append("Policy strictly denies PII modifications.")
                    return {
                        "decision": "DENY",
                        "explanation": " ".join(explanation)
                    }
                else:
                    explanation.append("PII modification requires additional approval.")
                    return {
                        "decision": "DENY",
                        "explanation": " ".join(explanation)
                    }

            blocked_columns = set(policy.get("blocked_columns", []))
            violated_blocked = sorted(accessed_columns & blocked_columns)
            if violated_blocked:
                explanation.append(
                    f"UPDATE operation cannot modify blocked column(s): {', '.join(violated_blocked)}."
                )
                return {
                    "decision": "DENY",
                    "columns_to_filter": violated_blocked,
                    "explanation": " ".join(explanation)
                }

            explanation.append("UPDATE operation passed basic governance checks.")

        else:
            if pii_accessed:
                explanation.append("Query accessed PII data.")

                if policy.get("deny_pii_access", False) or policy.get("deny_pii", False):
                    explanation.append("Policy denies access to PII data.")
                    return {
                        "decision": "DENY",
                        "explanation": " ".join(explanation)
                    }
                if policy.get("mask_pii", False):
                    explanation.append("Policy requires masking of PII data.")
                    return {
                        "decision": "ALLOW_WITH_MASKING",
                        "explanation": " ".join(explanation)
                    }

            allowed_tables = policy.get("allowed_tables", [])
            if allowed_tables:
                explanation.append("Table access restrictions configured but not yet implemented.")
                return {
                    "decision": "DENY",
                    "explanation": " ".join(explanation)
                }

            blocked_columns = set(policy.get("blocked_columns", []))
            violated_blocked = sorted(accessed_columns & blocked_columns)
            if violated_blocked:
                explanation.append(
                    f"Blocked column(s) will be filtered from results: {', '.join(violated_blocked)}."
                )
                return {
                    "decision": "ALLOW_WITH_FILTERING",
                    "columns_to_filter": violated_blocked,
                    "explanation": " ".join(explanation)
                }

        explanation.append("No policy violations detected.")
        return {
            "decision": "ALLOW",
            "explanation": " ".join(explanation)
        }

def suggest_remediation(decision: dict, sandbox_result: dict) -> dict:
    suggestions = []
    classifications = sandbox_result.get("column_classification", {})

    if decision['decision'] == "DENY":
        pii_columns = [col for col, c in classifications.items() if c == "PII"]
        if pii_columns:
            suggestions.append(f"Remove or mask PII columns: {', '.join(pii_columns)}")

    if decision['decision'] == "ALLOW_WITH_MASKING":
        suggestions.append("Apply masking to sensitive fields.")

    return {"suggestion": suggestions}