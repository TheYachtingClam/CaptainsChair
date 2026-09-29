from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration comes only from environment variables (REQ-OPS-04)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    site_password: str = Field(min_length=1)
    session_secret: str = Field(min_length=16)
    database_url: str = "sqlite:///./data/captains_chair.db"
    log_level: str = "info"
    # Directory holding the built React client. Served when it exists.
    static_dir: Path = Path(__file__).resolve().parent.parent / "static"
    # Set to false only for local HTTP development (no HTTPS).
    secure_cookies: bool = True
    session_days: int = 30
    login_attempts_per_minute: int = 5


@lru_cache
def get_settings() -> Settings:
    # Raises a validation error, and so refuses to start, if the password
    # or session secret is missing (REQ-AUTH-16).
    return Settings()
