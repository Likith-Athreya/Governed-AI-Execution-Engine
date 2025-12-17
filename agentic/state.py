from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_input: str
    sql: Optional[str]
    final_result: Optional[dict]