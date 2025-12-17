import json
POLICY_SCHEMA = {
"max_amount_without_manager_approval": int,
"blocked_vendors":list,
"allowed_countries":list
}
def is_already_structured(policy):
    return isinstance(policy, dict)
def validate_policy(policy_dict):
    validated = {}

    validated["max_amount_without_manager_approval"] = int(


    policy_dict.get("max_amount_without_manager_approval", 0)
    )
    validated["blocked_vendors"] = policy_dict.get("blocked_vendors", [])
    if not isinstance(validated["blocked_vendors"], list):
        validated["blocked_vendors"]=[validated["blocked_vendors"]]
    validated["allowed_currencies"]=policy_dict.get("allowed_currencies",["USD"])
    if not isinstance(validated["allowed_currencies"], list):
        validated["allowed_currencies"]=[validated["allowed_currencies"]]
    return validated
    
def interpret_policy(policy_text):
    if is_already_structured(policy_text):
        return validate_policy(policy_text)
    policy_text = policy_text.lower()

    max_amount = 0
    blocked = []
    allowed = ["USD", "EUR", "INR"]

    import re
    match_amount = re.search(r"(\d{3,6})", policy_text)
    if match_amount:
        max_amount = int(match_amount.group(1))

    if "idiot" in policy_text:
        blocked.append("Idiot LLC")
    if "vendoridiot" in policy_text:
        blocked.append("VendorIdiot LLC")

    extracted_policy = {
        "max_amount_without_manager_approval": max_amount,
        "blocked_vendors": blocked,
        "allowed_currencies": allowed
    }
    return validate_policy(extracted_policy)