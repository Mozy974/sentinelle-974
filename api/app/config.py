"""Sentinelle 974 — configuration."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://sentinelle:sentinelle@localhost:5433/sentinelle"
    ollama_base_url: str = "http://host.docker.internal:11434"
    sentinelle_host: str = "localhost"
    llm_model: str = Field(
        default="OpenLLM-France/Luciole-Instruct-1.1:1B",
        validation_alias="SENTINELLE_LLM_MODEL",
    )


settings = Settings()
