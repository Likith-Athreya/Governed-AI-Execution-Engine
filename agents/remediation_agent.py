class RemediationAgent:
    def suggest(self, decision: dict, sandbox_result: dict)-> dict:
        suggestions = []

        classifications = sandbox_result.get("column_classification", {})

        if decision['decision'] == "DENY":
            pii_columns = [ col for col, c in classifications.items() if c == "PII"]
            if pii_columns:
                suggestions.append(f"Remove or mask PII columns: {', '.join(pii_columns)}")

        if decision['decision'] == "ALLOW_WITH_MASKING":
            suggestions.append("Apply masking to sensitive fields.")

        return {"suggestion": suggestions}