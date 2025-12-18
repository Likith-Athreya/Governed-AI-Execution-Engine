from catalog.pii_classifier import PIIClassifier

class GovernanceDecisionAgent:
    def decide(self, sandbox_result: dict, policy: dict)-> dict:
        classifications = sandbox_result.get("column_classification", {})
        accessed_types = set(classifications.values())
        accessed_columns = set(sandbox_result.get("columns_accessed", []))
        explanation = []

        pii_accessed = "PII" in accessed_types
        
        if pii_accessed:
            explanation.append("Query accessed PII data.")
            
            # Deny if policy forbids PII access (support both legacy and new keys)
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

        # If any accessed column is blocked, allow but filter those columns from results
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