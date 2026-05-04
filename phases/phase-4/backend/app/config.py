from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "restaurant-reco-phase-4"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8400
    catalog_file: str = "phases/phase-1/backend/data/restaurants.normalized.json"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def catalog_path(self) -> Path:
        return Path(self.catalog_file).resolve()


settings = Settings()
