from .rule_engine import check_policy_rules
def simulate_decision(policy, invoice):
    violations = check_policy_rules(policy, invoice)
    return { 
        "would_violate":len(violations)>0,
        "violations": violations
    }