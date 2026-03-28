"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """NEXUS application settings."""

    supabase_url: str
    supabase_secret_key: str
    supabase_publishable_key: str
    google_api_key: str
    gemini_model_fast: str = "gemini-2.0-flash"
    gemini_model_pro: str = "gemini-2.0-pro"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
