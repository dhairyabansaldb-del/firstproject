from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "restaurant-reco-phase-5"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8500
    phase4_service_url: str = "http://127.0.0.1:8401"
    frontend_origin: str = "http://127.0.0.1:5500"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def phase4_recommendations_url(self) -> str:
        return f"{self.phase4_service_url}/recommendations"


settings = Settings()
