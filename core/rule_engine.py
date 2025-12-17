def check_policy_rules(policy, invoice):
    violations = []

    if invoice.get("vendor") in policy.get("blocked_vendors", []):
        violations.append(f"{invoice['vendor']} is blocked.")

    if invoice.get("amount", 0) > policy.get("max_amount_without_manager_approval", 0):
        violations.append(
            f"Amount {invoice['amount']} exceeds limit without manager approval."
        )

    if invoice.get("currency") not in policy.get("allowed_currencies", []):
        violations.append(
            f"Currency {invoice['currency']} is not allowed. Allowed: {policy.get('allowed_currencies', [])}."
        )

    return violations
