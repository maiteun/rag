from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://user:password@localhost:5432/experience_vault",
        alias="DATABASE_URL",
    )
    llm_provider: str = Field(default="fake", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4.1-mini", alias="LLM_MODEL")
    embedding_provider: str = Field(default="fake", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    notion_api_token: str | None = Field(default=None, alias="NOTION_API_TOKEN")
    notion_api_version: str = Field(default="2026-03-11", alias="NOTION_API_VERSION")


@lru_cache
def get_settings() -> Settings:
    return Settings()
