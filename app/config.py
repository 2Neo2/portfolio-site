from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ivan Doronin — Python Backend Developer"
    debug: bool = False
    content_dir: Path = BASE_DIR / "content"
    site_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
