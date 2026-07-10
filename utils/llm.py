"""
Single shared LLM instance for all agents. Provider-agnostic: whichever
model string is in GEMINI_MODEL (despite the name, it can be any
CrewAI/LiteLLM-supported model string) is what gets used. This means
switching from Gemini to OpenAI later is just an .env change:

    GEMINI_MODEL=openai/gpt-4o-mini
    OPENAI_API_KEY=sk-...

No code changes needed.
"""
from crewai import LLM
from config.settings import settings


def get_llm(temperature: float = 0.7) -> LLM:
    kwargs = {"model": settings.GEMINI_MODEL, "temperature": temperature}
    if settings.GEMINI_MODEL.startswith("gemini/"):
        kwargs["api_key"] = settings.GEMINI_API_KEY
    return LLM(**kwargs)