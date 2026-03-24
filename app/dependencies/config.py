from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Awesome FastAPI Demo"
    version: str = "1.0.0"
    database_url: str = "postgresql+psycopg2://app:app@127.0.0.1:5432/awesome_fastapi"
    jwt_secret: str = "change-me-in-production-use-32bytes!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()
