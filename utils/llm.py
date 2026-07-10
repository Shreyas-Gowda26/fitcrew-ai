"""
Single shared Gemini LLM instance for all agents. CrewAI routes this
through LiteLLM automatically since the model string is prefixed "gemini/".
"""
from crewai import LLM
from config.settings import settings


def get_llm(temperature: float = 0.7) -> LLM:
    return LLM(
        model=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY,
        temperature=temperature,
    )
