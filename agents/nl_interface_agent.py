import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API = os.getenv("GROQ_API_KEY")
model = "meta-llama/llama-4-maverick-17b-128e-instruct"
TEMPERATURE = 0.0

class NaturalLanguageAgent:
    def interpret(self, user_input: str, schema_hint: str)-> dict:
        prompt = f"""You are an enterprise data agent.

Convert the user request into a JSON action plan.

Rules:
- Output ONLY valid JSON
- No markdown
- No explanations
- SQL must be SELECT-only
- Do NOT execute anything
- Use safe, minimal queries
- If unsure, still propose SQL (governance will decide)

schema_hint: {schema_hint}
User Request: {user_input}
Return JSON with exactly these keys:
intent, action, sql
"""
        payload = {
            "model": model,
            "temperature": TEMPERATURE,
            "messages": [
                {
                    "role": "system",
                    "content": "You output JSON only. Never explain."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json = payload,
            timeout = 30
        )
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]

        try:
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            plan = json.loads(content)
        
        except json.JSONDecodeError:
            raise ValueError(f"LLM response is not valid JSON: {content}")
        
        return plan

