from typing import List, Dict
from pydantic import BaseModel, Field

class SQLPlan(BaseModel):
    intent: str = Field(description="User's intent or goal")
    action: str = Field(description="Action to take")
    sql: str = Field(description="SQL query (SELECT or UPDATE)")

class PolicyConfig(BaseModel):
    max_rows: int | None = Field(default=None, description="Maximum rows allowed")
    deny_pii: bool = Field(default=False, description="Deny access to PII data")
    blocked_columns: List[str] = Field(default_factory=list, description="List of blocked column names")
    allowed_tables: List[str] = Field(default_factory=list, description="List of allowed table names")

PII_KEYWORDS = ['name', 'email', 'phone', 'address', 'ssn', 'id']

def classify_columns(columns: List[str]) -> Dict[str, str]:
    """Classify columns for PII detection"""
    return {col: 'PII' if any(k in col.lower() for k in PII_KEYWORDS) else 'PUBLIC' for col in columns}