from langgraph.graph import StateGraph, END
from agentic.state import AgentState
from agentic.nodes import nl_to_sql_node, execute_sql_node

builder = StateGraph(AgentState)

builder.add_node("nl", nl_to_sql_node)
builder.add_node("execute_sql", execute_sql_node)

builder.set_entry_point("nl")
builder.add_edge("nl", "execute_sql")
builder.add_edge("execute_sql", END)

graph = builder.compile()