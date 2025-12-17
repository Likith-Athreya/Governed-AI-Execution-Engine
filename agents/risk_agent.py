class RiskAssessmentAgent:
    def assess(self, sandbox_result: dict)-> dict:
        risk_score = 0
        reasons = []

        classifications = sandbox_result.get("column_classification", {})
        rows = sandbox_result.get("rows_returned", 0)

        if "PII" in classifications.values():
            risk_score += 50
            reasons.append("Accessed PII data.")
        
        if rows > 1000:
            risk_score += 30
            reasons.append("Large number of rows returned.")

        if risk_score == 0:
            reasons.append("No significant risks detected.")
        
        return {
            "risk_score": risk_score,
            "reasons": reasons
        }