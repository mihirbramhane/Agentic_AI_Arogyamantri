"""Central configuration for AarogyaMitra backend.

All secrets come from environment variables (see .env.example).
Never hardcode API keys here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- LLM (CrewAI uses this via litellm) ---
    openai_api_key: str = ""
    llm_model: str = "gpt-4o"

    # --- Supabase (scheme DB + application tracking) ---
    supabase_url: str = ""
    supabase_service_key: str = ""

    # --- Google Places (empanelled hospital finder) ---
    google_places_api_key: str = ""

    # --- RAG vector store ---
    chroma_dir: str = "./data/chroma"
    scheme_docs_dir: str = "./data/scheme_docs"
    embedding_model: str = "text-embedding-3-small"

    # --- CORS: your Next.js origin ---
    frontend_origin: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
