"""
Single shared LLM instance for all agents. Provider-agnostic: whichever
model string is in GEMINI_MODEL (despite the name, it can be any
CrewAI/LiteLLM-supported model string) is what gets used. This means
switching providers later is just an .env change, no code changes:

    Gemini (default):
        GEMINI_MODEL=gemini/gemini-2.5-flash
        GEMINI_API_KEY=...

    OpenAI:
        GEMINI_MODEL=openai/gpt-4o-mini
        OPENAI_API_KEY=...

    OpenRouter:
        GEMINI_MODEL=openrouter/deepseek/deepseek-chat   # <provider>/<model> per OpenRouter's catalog
        OPENROUTER_API_KEY=...
"""
from crewai import LLM
from config.settings import settings

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_llm(temperature: float = 0.7) -> LLM:
    model = settings.GEMINI_MODEL
    kwargs = {"model": model, "temperature": temperature}

    if model.startswith("gemini/"):
        kwargs["api_key"] = settings.GEMINI_API_KEY
    elif model.startswith("openrouter/"):
        kwargs["api_key"] = settings.OPENROUTER_API_KEY
        kwargs["base_url"] = OPENROUTER_BASE_URL
    elif model.startswith("openai/"):
        kwargs["api_key"] = settings.OPENAI_API_KEY

    return LLM(**kwargs)