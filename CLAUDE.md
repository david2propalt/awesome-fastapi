# awesome-fastapi — Project Context

> 粘贴本文件内容到 Claude Project Instructions，使每次对话都能获得完整项目上下文。

---

## 项目简介

一个生产风格的 FastAPI 最小化演示项目，展示规范的分层架构、依赖注入、JWT 认证、统一错误处理和集成测试。

---

## 技术栈

| 层次 | 技术 |
|------|------|
| Web 框架 | FastAPI (sync handlers) |
| ORM | SQLAlchemy 2.0 (`Mapped` / `mapped_column`) |
| 数据库 | MySQL (pymysql 驱动) |
| Schema 校验 | Pydantic v2 (`ConfigDict`, `Field`) |
| 配置管理 | pydantic-settings (`BaseSettings`, `.env` 文件) |
| 认证 | JWT Bearer（PyJWT，HS256） |
| 测试 | pytest + httpx (`TestClient`) |
| Lint | ruff (line-length=100, py312, rules: E/F/I) |
| Python | ≥ 3.12 |

---

## 项目结构

```
awesome-fastapi/
├── app/
│   ├── main.py                  # FastAPI 实例、middleware、exception handler、router 注册
│   ├── api/
│   │   ├── auth.py              # POST /auth/login，返回 JWT token
│   │   ├── orders.py            # Order CRUD（需要认证）
│   │   ├── products.py          # Product CRUD（无需认证）
│   │   └── users.py             # User CRUD（无需认证）
│   ├── models/
│   │   ├── __init__.py          # 统一导出所有 Model（供 metadata 发现）
│   │   ├── order.py             # Order ORM 模型
│   │   ├── product.py           # Product ORM 模型
│   │   └── user.py              # User ORM 模型
│   ├── schemas/
│   │   ├── auth.py              # LoginRequest / TokenResponse
│   │   ├── order.py             # OrderCreate / OrderResponse
│   │   ├── product.py           # ProductCreate / ProductResponse
│   │   └── user.py              # UserCreate / UserResponse
│   ├── db/
│   │   └── session.py           # engine、SessionLocal、Base、get_db 依赖
│   ├── dependencies/
│   │   ├── auth.py              # get_current_user、create_access_token
│   │   └── config.py            # AppConfig (pydantic-settings) + get_config()
│   └── core/
│       └── errors.py            # 自定义 HTTPException 子类
├── tests/
│   ├── test_auth.py             # 认证集成测试
│   ├── test_orders.py           # Order API 集成测试（含 auth）
│   ├── test_products.py         # Product API 集成测试
│   └── test_users.py            # User API 集成测试
├── pyproject.toml
└── .env                         # 本地环境变量（不提交）
```

---

## 核心架构约定

### 1. 路由层 (`app/api/`)

- 每个资源一个文件，`router = APIRouter(prefix="/{resources}", tags=["{resources}"])`
- 同步 handler（不用 `async def`）
- 每个路由文件包含 `to_{resource}_response()` 转换函数，**不直接返回 ORM 对象**
- DELETE 返回 `Response(status_code=204)`，不返回 body

### 2. ORM 模型 (`app/models/`)

- 继承 `app.db.session.Base`
- **必须使用 SQLAlchemy 2.0 风格**：`Mapped[type]` 注解 + `mapped_column()`
- 可选字段类型写为 `Mapped[str | None]`
- String 字段必须指定长度：`String(100)`
- 新模型必须在 `app/models/__init__.py` 中导出，否则 `Base.metadata` 无法发现

### 3. Schema (`app/schemas/`)

- 每个资源两个 schema：`{Resource}Create` 和 `{Resource}Response`
- `Create`：`ConfigDict(extra="forbid")` + `Field(...)` 带校验约束
- `Response`：`ConfigDict(extra="ignore", from_attributes=True)` 支持 ORM 对象直接序列化

### 4. 错误处理 (`app/core/errors.py`)

- 自定义异常继承 `HTTPException`，集中定义，命名为 `{Resource}NotFoundError`
- `UnauthorizedError` 返回 401，携带 `WWW-Authenticate: Bearer` 响应头
- `main.py` 中注册了全局 exception handler，统一响应格式：
  ```json
  {
    "success": false,
    "error": { "code": 404, "message": "...", "path": "/orders/999" }
  }
  ```
- 成功响应直接返回 schema 对象（FastAPI 自动序列化），**不需要包 `success` 字段**

### 5. 认证 (`app/dependencies/auth.py`)

- `get_current_user(credentials, db, config)` — FastAPI 依赖，验证 Bearer token，返回当前 `User`
- `create_access_token(user_id, config)` — 生成 JWT，payload 包含 `sub`（user_id）和 `exp`
- `hash_password(plain)` — SHA-256 哈希，与 `app/api/users.py` 保持一致
- 需要认证的路由加 `_: User = Depends(get_current_user)`；无需认证的路由不加
- 无 token → 403；token 无效/过期 → 401

### 6. 数据库会话 (`app/db/session.py`)

- `get_db()` 是 FastAPI 依赖，每次请求创建/关闭 Session
- `engine` 创建时带 `pool_pre_ping=True`
- 测试通过 `app.dependency_overrides[get_db] = override_get_db` 替换为测试数据库

### 7. 配置 (`app/dependencies/config.py`)

- `AppConfig` 继承 `BaseSettings`，自动读取 `.env` 文件
- `get_config()` 用 `@lru_cache` 装饰，全局单例
- 关键配置：`database_url`、`app_name`、`version`、`jwt_secret`、`jwt_algorithm`、`jwt_expire_minutes`

---

## 命名规范

| 概念 | 规范 | 示例 |
|------|------|------|
| ORM 模型类 | PascalCase | `Order` |
| 数据库表名 | snake_case 复数 | `orders` |
| Schema 类 | `{Resource}Create` / `{Resource}Response` | `OrderCreate` |
| 自定义异常 | `{Resource}NotFoundError` | `OrderNotFoundError` |
| 路由转换函数 | `to_{resource}_response()` | `to_order_response()` |
| 路由变量 | `router` | `router = APIRouter(...)` |
| 测试函数 | `test_{action}_{resource}[_{case}]` | `test_get_order_not_found` |

---

## 测试规范

- 测试数据库：`awesome_fastapi_test`（独立于开发库）
- 通过 `TEST_DATABASE_URL` 环境变量覆盖连接串
- 每个测试函数前通过 `setup_function()` 执行 `drop_all` + `create_all` 保证隔离
- 使用 `fastapi.testclient.TestClient`（同步，不需要 `pytest-asyncio`）
- 测试直接断言 HTTP 状态码和响应 JSON 字段
- **需要认证的接口**：先 `POST /users/` 注册，再 `POST /auth/login` 获取 token，添加 `Authorization: Bearer <token>` header

---

## 添加新资源的完整步骤

1. `app/models/{resource}.py` — 创建 ORM 模型
2. `app/models/__init__.py` — 导出新模型
3. `app/schemas/{resource}.py` — 创建 Create + Response schema
4. `app/core/errors.py` — 添加 `{Resource}NotFoundError`
5. `app/api/{resource_plural}.py` — 创建路由文件（按需加 `Depends(get_current_user)`）
6. `app/main.py` — `include_router` 新路由，并导入模型（`noqa: F401`）
7. `tests/test_{resource_plural}.py` — 创建集成测试

---

## 常见陷阱

- `db.commit()` 后必须 `db.refresh(item)` 才能读取数据库生成的 `id`
- 旧版 `Column()` 与新版 `mapped_column()` 不可混用
- Pydantic v2 不再支持 `class Config`，必须用 `model_config = ConfigDict(...)`
- 路由 DELETE 不返回 body，测试中断言 `response.text == ""`
- `hash_password` 在 `app/api/users.py` 和 `app/dependencies/auth.py` 中各有一份，逻辑相同（SHA-256），修改时两处保持一致
