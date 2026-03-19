from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Awesome FastAPI Demo"
    version: str = "1.0.0"
    database_url: str = "mysql+pymysql://app:app@127.0.0.1:3306/awesome_fastapi"


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()
