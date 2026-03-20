# Awesome FastAPI Demo

A minimal production-style FastAPI demo with:
- clear project structure
- request validation via Pydantic
- RESTful CRUD-style endpoints
- JWT Bearer authentication
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
│   │   ├── auth.py             # Login endpoint
│   │   ├── orders.py           # Order CRUD routes (auth required)
│   │   ├── products.py         # Product CRUD routes
│   │   └── users.py            # User CRUD routes
│   ├── core/
│   │   └── errors.py           # Custom HTTP exceptions
│   ├── db/
│   │   └── session.py          # SQLAlchemy engine/session/get_db
│   ├── dependencies/
│   │   ├── auth.py             # JWT auth dependency (get_current_user)
│   │   └── common.py           # App-level dependency injection
│   ├── models/
│   │   ├── __init__.py         # Unified model exports
│   │   ├── order.py            # Order ORM model
│   │   ├── product.py          # Product ORM model
│   │   └── user.py             # User ORM model
│   ├── schemas/
│   │   ├── auth.py             # LoginRequest / TokenResponse schemas
│   │   ├── order.py            # Order request/response schemas
│   │   ├── product.py          # Product request/response schemas
│   │   └── user.py             # User request/response schemas
│   └── main.py                 # FastAPI app entrypoint
├── tests/
│   ├── test_auth.py            # Auth integration tests
│   ├── test_orders.py          # Order API integration tests
│   ├── test_products.py        # Product API integration tests
│   └── test_users.py           # User API integration tests
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
| `JWT_SECRET` | `change-me-in-production` | Secret key for signing JWT tokens — **change in production** |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `60` | Token expiry in minutes |

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

### Public (no auth required)

- `GET /` — health check
- `POST /users/` — create user
- `GET /users/{user_id}` — fetch user
- `PUT /users/{user_id}` — update user
- `DELETE /users/{user_id}` — delete user (soft delete, 204)
- `POST /auth/login` — obtain JWT token
- `POST /products/` — create product
- `GET /products/{product_id}` — fetch product
- `PUT /products/{product_id}` — update product
- `DELETE /products/{product_id}` — delete product (204)

### Protected (Bearer token required)

- `POST /orders/` — create order
- `GET /orders/{order_id}` — fetch order
- `PUT /orders/{order_id}` — update order
- `DELETE /orders/{order_id}` — delete order (204)

### Docs

- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc

## Authentication Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/users/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'

# 2. Login → get token
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "password": "secret123"}'

# 3. Call protected endpoint
curl http://localhost:8000/orders/1 \
  -H 'Authorization: Bearer <access_token>'
```
