"""
Centralized configuration. Everything else in the app imports from here
instead of calling os.getenv() directly, so there's exactly one place
that knows about environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "fitcrew_ai")

    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "me")

    @classmethod
    @classmethod
    def validate(cls):
        missing = []
        if not cls.MONGO_URI:
            missing.append("MONGO_URI")

        if cls.GEMINI_MODEL.startswith("gemini/") and not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        elif cls.GEMINI_MODEL.startswith("openrouter/") and not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        elif cls.GEMINI_MODEL.startswith("openai/") and not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Copy .env.example to .env and fill these in."
            )


settings = Settings()
