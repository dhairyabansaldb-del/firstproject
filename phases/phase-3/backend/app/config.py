from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "restaurant-reco-phase-3"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8300
    catalog_file: str = "phases/phase-2/backend/data/restaurants.normalized.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def catalog_path(self) -> Path:
        return Path(self.catalog_file).resolve()


settings = Settings()
