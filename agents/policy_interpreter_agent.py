import json
from agents.llm_wrapper import get_llm, call_llm, DEFAULT_MODEL
from langchain_core.prompts import ChatPromptTemplate

class PolicyInterpreterAgent:
    def __init__(self):
        self.llm = get_llm(DEFAULT_MODEL, 0.0)

    def interpret(self, policy_text: str) -> dict:
        from agents.tools import PolicyConfig

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Convert policy text into structured policy configuration."),
            ("human", "Policy text: {policy_text}")
        ])

        chain = prompt | self.llm.with_structured_output(PolicyConfig)
        result = chain.invoke({"policy_text": policy_text})

        return {
            "max_rows": result.max_rows,
            "deny_pii": result.deny_pii,
            "blocked_columns": result.blocked_columns,
            "allowed_tables": result.allowed_tables
        }

    def explain_effect(self, policy, simulation, decision) -> str:
        prompt = f"""Analyze how this policy affects SQL queries:

Policy: {json.dumps(policy, indent=2)}
Query: {simulation.get('query_type', 'Unknown')} accessing {simulation.get('columns_accessed', [])} columns, {simulation.get('rows_returned', 0)} rows
Decision: {decision.get('status', 'Unknown')}

Explain: which queries fail, what data becomes unavailable, and the business impact. Be specific and concise.
"""

        content = call_llm(
            prompt=prompt,
            system_prompt="Explain clearly in plain English. No JSON.",
            model=DEFAULT_MODEL,
            temperature=0.2,
        )

        return content.strip()