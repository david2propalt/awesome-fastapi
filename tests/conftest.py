from typing import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base, get_db
from app.main import app


class TestConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    test_database_url: str = "postgresql+psycopg2://app:app@127.0.0.1:5432/awesome_fastapi_test"


TEST_DATABASE_URL = TestConfig().test_database_url

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _override_get_db() -> Generator[Session, None, None]:
    db = _session_factory()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
