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
        prompt = f"""
        You are a governance assistant.
        explain in 2 to 3 sentences, in plain english, how the following POLICY would affect the DATA returned by the QUERY.

        Be specific about:
        - columns that would be removed, masked, or blocked
        - Row limits that would apply
        - Whether the query is allowed or denied and why
        POLICY (JSON):
        {json.dumps(policy, indent=2)}

        SIMULATION (JSON):
        {json.dumps(simulation, indent=2)}

        DECISION (JSON):
        {json.dumps(decision, indent=2)}
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