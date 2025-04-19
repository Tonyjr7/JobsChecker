from pathlib import Path

from decouple import config
from pydantic_settings import BaseSettings

# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Class to hold application's config values."""

    GROQ_API_KEY: str = config("GROQ_API_KEY", default="")
    GEMINI_API_KEY: str = config("GEMINI_API_KEY", default="")


settings = Settings()