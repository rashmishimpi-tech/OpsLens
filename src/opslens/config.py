from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpsLens API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    database_url: str = "postgresql+psycopg://opslens:opslens@localhost:5432/opslens"
    mlflow_database_url: str | None = None
    airflow_database_url: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@cache
def get_settings() -> Settings:
    return Settings()
