class GovernanceDecisionAgent:
    def decide(self, sandbox_result: dict, policy: dict)-> dict:
        classifications = sandbox_result.get("column_classification", {})
        accessed_types = set(classifications.values())
        explanation = []

        if "PII" in accessed_types:
            explanation.append("Query accessed PII data.")
        
        if policy.get("deny_pii_access", False):
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
        explanation.append("No policy violations detected.")
        return {
            "decision": "ALLOW",
            "explanation": " ".join(explanation)
        }