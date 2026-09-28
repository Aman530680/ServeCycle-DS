"""
Application settings loaded from environment variables / .env file.
"""

from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "servecycle"
    db_user: str = "root"
    db_password: str = ""

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    model_path: str = "models/random_forest.joblib"
    model_metadata_path: str = "models/model_metadata.json"
    random_state: int = 42
    default_service_level: float = 0.90

    clean_csv_path: str = "data/processed/clean_events.csv"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
