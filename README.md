# Awesome FastAPI Demo

A minimal production-style FastAPI demo with:
- clear project structure
- request validation via Pydantic
- RESTful CRUD-style endpoints
- CORS middleware
- dependency injection example
- unified JSON error responses
- MySQL persistence with SQLAlchemy
- environment-based configuration via pydantic-settings

## Runtime Requirement

- Python 3.12+

## Project Structure

```text
awesome-fastapi/
├── app/
│   ├── api/
│   │   └── items.py            # Item CRUD routes
│   ├── core/
│   │   └── errors.py           # Custom HTTP exceptions
│   ├── db/
│   │   └── session.py          # SQLAlchemy engine/session/get_db
│   ├── dependencies/
│   │   └── common.py           # App-level dependency injection
│   ├── models/
│   │   └── item.py             # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── item.py             # Pydantic request/response schemas
│   └── main.py                 # FastAPI app entrypoint
├── tests/
│   └── test_api.py             # API integration tests (MySQL-backed)
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions: ruff + pytest
├── pyproject.toml              # Dependencies and tool configuration
├── uv.lock                     # Locked dependency graph (uv)
├── .env.example                # Environment variable reference
└── README.md
```

## Local MySQL Bootstrap (recommended)

```sql
CREATE DATABASE IF NOT EXISTS awesome_fastapi;
CREATE DATABASE IF NOT EXISTS awesome_fastapi_test;
CREATE USER IF NOT EXISTS 'app'@'%' IDENTIFIED BY 'app';
CREATE USER IF NOT EXISTS 'app_test'@'%' IDENTIFIED BY 'app_test';
GRANT ALL PRIVILEGES ON awesome_fastapi.* TO 'app'@'%';
GRANT ALL PRIVILEGES ON awesome_fastapi_test.* TO 'app_test'@'%';
FLUSH PRIVILEGES;
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Awesome FastAPI Demo` | Application name |
| `VERSION` | `1.0.0` | Application version |
| `DATABASE_URL` | `mysql+pymysql://app:app@127.0.0.1:3306/awesome_fastapi` | SQLAlchemy database URL |

## Run (uv)

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Development (uv)

```bash
uv run ruff check .
TEST_DATABASE_URL='mysql+pymysql://app_test:app_test@127.0.0.1:3306/awesome_fastapi_test' uv run pytest
```

## Endpoints

- `GET /` health check
- `POST /items/` create item
- `GET /items/{item_id}` fetch item by id
- `PUT /items/{item_id}` update item
- `DELETE /items/{item_id}` delete item (204 No Content)
- `GET /docs` Swagger UI
- `GET /redoc` ReDoc
