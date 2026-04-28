from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    api_key: str
    api_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8")


settings = Settings()
