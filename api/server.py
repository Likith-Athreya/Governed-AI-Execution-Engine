from fastapi import FastAPI
from pydantic import BaseModel
import json

from agents.policy_interpreter import interpret_policy
from core.decision import final_decision

app = FastAPI(title = "Autonomous Compliance and Audit Agent API")

class PolicyRequest(BaseModel):
    text: str
class InvoiceRequest(BaseModel):
    policy_text: str
    invoice: dict

@app.post("/interpret_policy")
def interpret(policy: PolicyRequest):
    structured = interpret_policy(policy.text)
    return{"structured_policy": structured}

@app.post("/simulate_invoice")
def simulate_endpoint(invoice_req:InvoiceRequest):
    policy = interpret_policy(invoice_req.policy_text)
    result = final_decision(policy, invoice_req.invoice)
    return result

@app.get("/")
def root():
    return {"message": "Welcome to the Autonomous Compliance and Audit Agent API"}