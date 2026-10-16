from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """App settings, loaded from environment variables or backend/.env."""

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    groq_api_key: str = ""
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-5-5"

    data_dir: Path = BACKEND_DIR / "data"


settings = Settings()
