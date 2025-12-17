from .simulation import simulate_decision
from .audit_logger import log_decision

def final_decision(policy, invoice):
    sim = simulate_decision(policy, invoice)

    decision = "FLAG" if sim["would_violate"] else "APPROVE"
    
    log_decision(policy, invoice, decision, sim["violations"])

    return {
        "decision": decision,
        "explanation": sim["violations"]
    }
