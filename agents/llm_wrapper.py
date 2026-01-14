import os
from typing import List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

def _build_groq_llm(model: str, temperature: float) -> ChatGroq:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set")

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=model,
        temperature=temperature,
    )

def get_llm(model: str = DEFAULT_MODEL, temperature: float = 0.0) -> ChatGroq:
    return _build_groq_llm(model, temperature)

def call_llm(
    *,
    prompt: str,
    system_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> str:
    messages: List = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt),
    ]

    groq_llm = _build_groq_llm(model=model, temperature=temperature)
    response = groq_llm.invoke(messages)
    return response.content