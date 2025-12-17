from fastapi import FastAPI
from pydantic import BaseModel
from agentic.graph import graph
from core.audit_logger import init_db
import json

init_db()

app = FastAPI(
    title = "Governed AI Execution Engine",
    description = "Natural language driven, policy-governed AI execution system",
    version = "1.0"
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def run_query(request: QueryRequest):
    result = graph.invoke({
        "user_input": request.query
    })

    return result["final_result"]

@app.get("/")
def root():
    return {"message": "Welcome to the Governed AI Execution Engine API"}
