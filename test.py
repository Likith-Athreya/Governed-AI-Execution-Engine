from agentic.governance_orchestrator import GovernanceOrchestrator

sandbox_output = {
    "columns_accessed": ["email", "ssn"],
    "column_classification": {
        "email": "PII",
        "ssn": "PII"
    },
    "rows_returned": 120
}

policy = {
    "deny_pii_access": True,
    "mask_pii": False
}

orchestrator = GovernanceOrchestrator()
result = orchestrator.run(sandbox_output, policy)

print("\n--- DAY 8 GOVERNANCE RESULT ---")
print(result)
