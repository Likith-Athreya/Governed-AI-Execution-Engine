from agents.llm_wrapper import get_llm, DEFAULT_MODEL
from agents.tools import SQLPlan
from langchain_core.prompts import ChatPromptTemplate

class NaturalLanguageAgent:
    def __init__(self):
        self.llm = get_llm(DEFAULT_MODEL, 0.0)

    def interpret(self, user_input: str, schema_hint: str) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an enterprise data agent. Convert user requests into SQL queries.
Rules:
- SQL can be SELECT or UPDATE queries
- Use safe, minimal queries
- If unsure, still propose SQL (governance will decide)
- Schema: {schema_hint}

{format_instructions}"""),
            ("human", "User Request: {user_input}")
        ])

        chain = prompt | self.llm.with_structured_output(SQLPlan)
        result = chain.invoke({
            "user_input": user_input,
            "schema_hint": schema_hint,
            "format_instructions": SQLPlan.schema_json()
        })

        return {
            "intent": result.intent,
            "action": result.action,
            "sql": result.sql
        }