import os
import json
import requests

GROQ_API = os.getenv("GROQ_API_KEY")
model = "meta-llama/llama-4-maverick-17b-128e-instruct"

class PolicyInterpreterAgent:
    def interpret(self, policy_text: str)-> dict:
        prompt = f"""
You are an enterprise governance policy interpreter.

Convert the policy into STRICT JSON.
Rules:
- Output ONLY valid JSON
- No markdown
- No explanations
- Use only these keys:
  - max_rows (int or null)
  - deny_pii (boolean)
  - blocked_columns (array of strings)
  - allowed_tables (array of strings)

Policy:
{policy_text}
"""

        payload = {
            "model": model,
            "temperature": 0.0,
            "messages": [
                    {"role": "system", "content": "Return JSON output only"},
                    {"role": "user", "content": prompt}
                ]
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json"
        }

        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]

        return json.loads(content)

    def explain_effect(self, policy, simulation, decision) -> str:
        prompt = f"""You are a senior data governance consultant analyzing the impact of a SQL query access policy.

**POLICY TO ANALYZE:**
{json.dumps(policy, indent=2)}

**DATABASE SCHEMA:**
- accounts(id, account_name, account_type, currency, balance, risk_level, created_at)
- vendors(id, vendor_name, country, is_blocked, risk_score, created_at)
- transactions(id, account_id, vendor_id, amount, currency, transaction_type, category, transaction_date, approved_by)
- budgets(id, department, category, monthly_limit, fiscal_year)

**PII COLUMNS:** balance (financial data), risk_level (sensitive ratings)

**SIMULATION RESULTS:**
- Query type: {simulation.get('query_type', 'Unknown')}
- Rows returned: {simulation.get('rows_returned', 0)}
- Columns accessed: {simulation.get('columns_accessed', [])}
- Decision: {decision.get('status', 'Unknown')}

**DEEP ANALYSIS REQUIREMENTS:**
Analyze this policy's impact on SQL queries with specific examples:

1. **Column Blocking Impact**: Which specific columns from which tables would be inaccessible? Give concrete examples of queries that would fail.

2. **PII Access Analysis**: If deny_pii is true, explain which customer data becomes unavailable and why this matters for business intelligence.

3. **Row Limit Effects**: If max_rows is set, explain how this affects large dataset analysis and reporting workflows.

4. **Table Access Restrictions**: If allowed_tables is not empty, explain which business processes lose data access.

5. **Query Modification Needs**: What specific changes would developers need to make to existing queries?

6. **Business Process Disruption**: Which specific business functions (customer analytics, vendor risk assessment, financial reporting) are most affected?

7. **Workaround Strategies**: What alternative approaches would be needed to achieve the same business objectives?

8. **Risk Mitigation vs. Functionality Trade-offs**: Is this policy's security benefit worth the operational cost?

Provide specific, evidence-based analysis referencing the actual database schema and query patterns. Avoid generic statements.
"""


        payload = {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "Explain clearly in plain English. No JSON."},
                {"role": "user", "content": prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json",
        }

        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"].strip()
        return content
