from agents.nl_interface_agent import NaturalLanguageAgent
from agents.policy_interpreter import interpret_policy, format_policy_for_llm
from execution.execution_kernel import ExecutionKernel
import json

policy = interpret_policy(json.load(open("data/policies/policy.json")))

nl_agent = NaturalLanguageAgent()
kernel = ExecutionKernel(policy)

def nl_to_sql_node(state: dict):
    schema_hint = "Table: customers (id, name, email, ssn, salary)"
    policy_context = format_policy_for_llm(policy)
    plan = nl_agent.interpret(state["user_input"], schema_hint, policy_context)
    return {"sql": plan["sql"]}

def execute_sql_node(state: dict):
    result = kernel.run_sql(state["sql"])
    return {"final_result": result}

