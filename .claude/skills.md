# Claude Skill Templates — awesome-fastapi

All templates follow the project's actual code style:
- SQLAlchemy 2.0 (`Mapped` / `mapped_column`)
- Pydantic v2 (`ConfigDict`, `Field`)
- Sync FastAPI route handlers
- `to_{resource}_response()` converter pattern
- Custom `HTTPException` subclasses in `app/core/errors.py`
- Uniform JSON envelope `{"success": True, ...}` / `{"success": False, "error": {...}}`

Variables are marked as `{{variable_name}}`.

---

## gen-resource

**用途**: 为全新资源一步生成模型、Schema、错误类、路由，并完成注册。

**使用示例**: `请用 gen-resource 生成 {{resource}} 资源，字段为 {{fields}}`

**模板**:

```
请为 {{resource}} 资源按顺序创建以下所有文件，严格遵循项目风格。

变量：
- resource         = {{resource}}          （单数 snake_case，如 order）
- resource_plural  = {{resource_plural}}   （复数 snake_case，如 orders）
- Resource         = {{Resource}}          （PascalCase，如 Order）
- 字段列表          = {{fields}}            （格式：字段名:类型，如 title:str, price:float）

步骤 1 — app/models/{{resource}}.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class {{Resource}}(Base):
    __tablename__ = "{{resource_plural}}"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # str 字段：Mapped[str] = mapped_column(String(N), nullable=False)
    # 可选字段：Mapped[str | None] = mapped_column(String(N), nullable=True)
    # 数值字段：Mapped[float] = mapped_column(nullable=False)

步骤 2 — app/schemas/{{resource}}.py
from pydantic import BaseModel, ConfigDict, Field

class {{Resource}}Create(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # 必填 str：Field(..., min_length=1, max_length=N)
    # 可选 str：Field(default=None, max_length=N)
    # 数值：Field(..., gt=0)

class {{Resource}}Response(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)
    id: int
    # 与模型字段一一对应

步骤 3 — app/core/errors.py 追加
class {{Resource}}NotFoundError(HTTPException):
    def __init__(self, {{resource}}_id: int) -> None:
        super().__init__(status_code=404, detail=f"{{Resource}} {{{resource}}_id} not found")

步骤 4 — app/api/{{resource_plural}}.py
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.core.errors import {{Resource}}NotFoundError
from app.db.session import get_db
# 若路由需要认证，取消下面两行注释：
# from app.dependencies.auth import get_current_user
# from app.models.user import User
from app.models.{{resource}} import {{Resource}}
from app.schemas.{{resource}} import {{Resource}}Create, {{Resource}}Response

router = APIRouter(prefix="/{{resource_plural}}", tags=["{{resource_plural}}"])

def to_{{resource}}_response({{resource}}: {{Resource}}) -> {{Resource}}Response:
    return {{Resource}}Response(id={{resource}}.id, ...)

@router.post("/", response_model={{Resource}}Response, status_code=201)
def create_{{resource}}(
    payload: {{Resource}}Create,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> {{Resource}}Response:
    {{resource}} = {{Resource}}(**payload.model_dump())
    db.add({{resource}})
    db.commit()
    db.refresh({{resource}})
    return to_{{resource}}_response({{resource}})

@router.get("/{{{resource}}_id}", response_model={{Resource}}Response)
def get_{{resource}}(
    {{resource}}_id: int,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> {{Resource}}Response:
    {{resource}} = db.get({{Resource}}, {{resource}}_id)
    if {{resource}} is None:
        raise {{Resource}}NotFoundError({{resource}}_id)
    return to_{{resource}}_response({{resource}})

@router.put("/{{{resource}}_id}", response_model={{Resource}}Response)
def update_{{resource}}(
    {{resource}}_id: int,
    payload: {{Resource}}Create,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> {{Resource}}Response:
    {{resource}} = db.get({{Resource}}, {{resource}}_id)
    if {{resource}} is None:
        raise {{Resource}}NotFoundError({{resource}}_id)
    for key, value in payload.model_dump().items():
        setattr({{resource}}, key, value)
    db.commit()
    db.refresh({{resource}})
    return to_{{resource}}_response({{resource}})

@router.delete("/{{{resource}}_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{{resource}}(
    {{resource}}_id: int,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> Response:
    {{resource}} = db.get({{Resource}}, {{resource}}_id)
    if {{resource}} is None:
        raise {{Resource}}NotFoundError({{resource}}_id)
    db.delete({{resource}})
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

步骤 5 — app/models/__init__.py 追加
from app.models.{{resource}} import {{Resource}}
# 加入 __all__

步骤 6 — app/main.py 追加
from app.api.{{resource_plural}} import router as {{resource_plural}}_router
from app.models import ..., {{Resource}}  # noqa: F401
app.include_router({{resource_plural}}_router)
```

---

## gen-router

**用途**: 为新资源生成完整的 CRUD API 路由文件。

**使用示例**: `请用 gen-router 为 {{resource}} 资源生成路由`

**模板**:

```
请在 app/api/{{resource_plural}}.py 创建以下内容，严格遵循项目风格：

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.errors import {{Resource}}NotFoundError
from app.db.session import get_db
from app.models.{{resource}} import {{Resource}}
from app.schemas.{{resource}} import {{Resource}}Create, {{Resource}}Response

router = APIRouter(prefix="/{{resource_plural}}", tags=["{{resource_plural}}"])

# 若路由需要认证，取消下面两行注释：
# from app.dependencies.auth import get_current_user
# from app.models.user import User


def to_{{resource}}_response({{resource}}: {{Resource}}) -> {{Resource}}Response:
    return {{Resource}}Response(
        id={{resource}}.id,
        {{field1}}={{resource}}.{{field1}},
        {{field2}}={{resource}}.{{field2}},
    )


@router.post("/", response_model={{Resource}}Response, status_code=201)
def create_{{resource}}(
    payload: {{Resource}}Create,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> {{Resource}}Response:
    {{resource}} = {{Resource}}(
        {{field1}}=payload.{{field1}},
        {{field2}}=payload.{{field2}},
    )
    db.add({{resource}})
    db.commit()
    db.refresh({{resource}})
    return to_{{resource}}_response({{resource}})


@router.get("/{{{resource}}_id}", response_model={{Resource}}Response)
def get_{{resource}}(
    {{resource}}_id: int,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> {{Resource}}Response:
    {{resource}} = db.get({{Resource}}, {{resource}}_id)
    if {{resource}} is None:
        raise {{Resource}}NotFoundError({{resource}}_id)
    return to_{{resource}}_response({{resource}})


@router.put("/{{{resource}}_id}", response_model={{Resource}}Response)
def update_{{resource}}(
    {{resource}}_id: int,
    payload: {{Resource}}Create,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> {{Resource}}Response:
    {{resource}} = db.get({{Resource}}, {{resource}}_id)
    if {{resource}} is None:
        raise {{Resource}}NotFoundError({{resource}}_id)

    {{resource}}.{{field1}} = payload.{{field1}}
    {{resource}}.{{field2}} = payload.{{field2}}

    db.commit()
    db.refresh({{resource}})
    return to_{{resource}}_response({{resource}})


@router.delete("/{{{resource}}_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{{resource}}(
    {{resource}}_id: int,
    db: Session = Depends(get_db),
    # _: User = Depends(get_current_user),  # 需要认证时取消注释
) -> Response:
    {{resource}} = db.get({{Resource}}, {{resource}}_id)
    if {{resource}} is None:
        raise {{Resource}}NotFoundError({{resource}}_id)

    db.delete({{resource}})
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

然后在 app/main.py 中 include 这个 router：
from app.api.{{resource_plural}} import router as {{resource_plural}}_router
app.include_router({{resource_plural}}_router)

同时在 app/models/__init__.py 中导出该模型（避免 SQLAlchemy metadata 遗漏）。
```

---

## gen-model

**用途**: 生成 SQLAlchemy 2.0 风格的 ORM 模型。

**使用示例**: `请用 gen-model 为 {{resource}} 生成模型，字段为 {{fields}}`

**模板**:

```
请在 app/models/{{resource}}.py 创建以下 SQLAlchemy 2.0 模型：

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class {{Resource}}(Base):
    __tablename__ = "{{resource_plural}}"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    {{field1}}: Mapped[str] = mapped_column(String({{max_length}}), nullable=False)
    {{field2}}: Mapped[str | None] = mapped_column(String({{max_length}}), nullable=True)
    {{field3}}: Mapped[float] = mapped_column(nullable=False)

规范：
- 必须继承 app.db.session.Base
- 使用 Mapped[type] 注解 + mapped_column()（SQLAlchemy 2.0 风格）
- nullable 字段类型写为 Mapped[str | None]
- String 字段必须指定长度上限
- __tablename__ 使用 snake_case 复数
```

---

## gen-schema

**用途**: 生成 Pydantic v2 的 Create / Response schema 对。

**使用示例**: `请用 gen-schema 为 {{resource}} 生成 schema`

**模板**:

```
请在 app/schemas/{{resource}}.py 创建以下 Pydantic v2 schema：

from pydantic import BaseModel, ConfigDict, Field


class {{Resource}}Create(BaseModel):
    model_config = ConfigDict(extra="forbid")

    {{field1}}: str = Field(..., min_length=1, max_length={{max_length}})
    {{field2}}: str | None = Field(default=None, max_length={{max_length}})
    {{field3}}: float = Field(..., gt=0)


class {{Resource}}Response(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int
    {{field1}}: str
    {{field2}}: str | None = None
    {{field3}}: float

规范：
- Create schema 使用 extra="forbid" 拒绝多余字段
- Response schema 使用 extra="ignore" + from_attributes=True（支持 ORM 对象）
- 必填字段用 Field(...) 并加校验（min_length/gt 等）
- 可选字段用 str | None，default=None
```

---

## gen-test

**用途**: 为新资源的 CRUD 路由生成完整测试文件。

**使用示例**: `请用 gen-test 为 {{resource}} 路由生成测试`

**模板**:

```
请在 tests/test_{{resource_plural}}.py 创建以下测试，遵循项目测试风格。
DB 引擎、client fixture、reset_db autouse fixture 均已在 tests/conftest.py 中定义，无需在此文件重复。

# 若路由需要认证，setup 中额外获取 auth_headers（参考 test_orders.py）

import pytest
from fastapi.testclient import TestClient

{{RESOURCE_PAYLOAD}} = {
    "{{field1}}": "{{sample_value1}}",
    "{{field2}}": "{{sample_value2}}",
    "{{field3}}": {{sample_number}},
}


class Test{{Resource}}s:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client
        # 若路由需要认证，在此注册用户并登录：
        # self.client.post("/users/", json={...})
        # resp = self.client.post("/auth/login", json={...})
        # self.auth_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    def test_create_{{resource}}(self) -> None:
        response = self.client.post("/{{resource_plural}}/", json={{RESOURCE_PAYLOAD}})
        # headers=self.auth_headers  # 需要认证时添加

        assert response.status_code == 201
        payload = response.json()
        assert isinstance(payload["id"], int)
        assert payload["{{field1}}"] == "{{sample_value1}}"

    def test_get_{{resource}}_by_id(self) -> None:
        created = self.client.post("/{{resource_plural}}/", json={{RESOURCE_PAYLOAD}})
        resource_id = created.json()["id"]

        response = self.client.get(f"/{{resource_plural}}/{resource_id}")

        assert response.status_code == 200
        assert response.json()["{{field1}}"] == "{{sample_value1}}"

    def test_get_{{resource}}_not_found(self) -> None:
        response = self.client.get("/{{resource_plural}}/999")

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_update_{{resource}}(self) -> None:
        created = self.client.post("/{{resource_plural}}/", json={{RESOURCE_PAYLOAD}})
        resource_id = created.json()["id"]

        response = self.client.put(
            f"/{{resource_plural}}/{resource_id}",
            json={"{{field1}}": "Updated", "{{field2}}": "New desc", "{{field3}}": {{sample_number2}}},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == resource_id
        assert payload["{{field1}}"] == "Updated"

    def test_update_{{resource}}_not_found(self) -> None:
        response = self.client.put(
            "/{{resource_plural}}/999",
            json={"{{field1}}": "X", "{{field2}}": None, "{{field3}}": 1.0},
        )

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_delete_{{resource}}(self) -> None:
        created = self.client.post("/{{resource_plural}}/", json={{RESOURCE_PAYLOAD}})
        resource_id = created.json()["id"]

        delete_response = self.client.delete(f"/{{resource_plural}}/{resource_id}")
        assert delete_response.status_code == 204
        assert delete_response.text == ""

        get_response = self.client.get(f"/{{resource_plural}}/{resource_id}")
        assert get_response.status_code == 404

    def test_delete_{{resource}}_not_found(self) -> None:
        response = self.client.delete("/{{resource_plural}}/999")

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404
```

---

## code-review

**用途**: 对指定文件或 diff 进行代码审查，关注项目规范符合性。

**使用示例**: `请用 code-review 审查 {{file_path}}`

**模板**:

```
请审查以下代码，按项目规范逐项检查：

[粘贴代码或文件路径]

检查清单：

**正确性**
- [ ] 路由 status_code 与语义一致（POST→201，DELETE→204，GET/PUT→200）
- [ ] 404 统一通过 app/core/errors.py 中的自定义异常抛出，不直接 raise HTTPException
- [ ] db.commit() 后必须 db.refresh() 才能读取数据库生成值（如 id）
- [ ] 测试使用 class + pytest fixture，DB 隔离由 conftest.py 的 reset_db autouse fixture 保证
- [ ] test_create 断言 id 用 isinstance(payload["id"], int)，不硬编码 == 1

**代码风格**
- [ ] SQLAlchemy 使用 Mapped[type] + mapped_column()，不用旧版 Column()
- [ ] Pydantic v2：使用 model_config = ConfigDict(...)，不用 class Config
- [ ] Create schema 有 extra="forbid"；Response schema 有 from_attributes=True
- [ ] 路由文件有 to_{resource}_response() 转换函数，不直接返回 ORM 对象
- [ ] update handler 中 db.get() 返回的对象已被 Session 追踪，直接改属性后 commit，不需要 db.add()
- [ ] 行宽 ≤ 100 字符（ruff line-length=100）

**安全性**
- [ ] 无 SQL 字符串拼接，全部通过 ORM 操作
- [ ] Create schema 的 extra="forbid" 防止字段注入
- [ ] 需要认证的路由加 `_: User = Depends(get_current_user)`，不需要认证的路由不加
- [ ] HTTPBearer 使用 auto_error=False，401 由 UnauthorizedError 统一抛出，不依赖框架默认行为

**可维护性**
- [ ] 新 router 已在 app/main.py 中 include
- [ ] 新 Model 已在 app/models/__init__.py 中导出

输出格式：先列出问题（文件:行号 + 说明），再给出修改建议。
```

---

## sql-optimize

**用途**: 审查并优化 SQLAlchemy ORM 查询，发现 N+1、缺失索引等问题。

**使用示例**: `请用 sql-optimize 优化 {{file_path}} 中的查询`

**模板**:

```
请分析以下 SQLAlchemy 查询代码，识别性能问题并给出优化建议：

[粘贴查询代码]

分析维度：

1. **N+1 查询**
   - 是否在循环中调用 db.get() 或访问关联属性？
   - 建议使用 selectinload / joinedload 预加载关联

2. **缺失索引**
   - 高频过滤字段（WHERE 条件字段）是否有 index=True？
   - 参考现有模型：id 字段已有 primary_key + index

3. **全表扫描**
   - 列表查询是否缺少 .limit() / .offset() 分页？
   - 建议模式：db.scalars(select({{Resource}}).limit(limit).offset(offset)).all()

4. **不必要的列加载**
   - 若只需部分字段，用 select({{Resource}}.id, {{Resource}}.name) 代替 select({{Resource}})

5. **项目约定一致性**
   - 单条查询用 db.get(Model, id)（已有主键走缓存）
   - 条件查询用 db.scalars(select(Model).where(...)).first()

输出：问题描述 + 优化后的代码片段。
```

---

## debug

**用途**: 系统化分析 Bug，定位根因并给出修复方案。

**使用示例**: `请用 debug 分析以下报错：{{error_message}}`

**模板**:

```
请分析以下问题，结合项目代码给出诊断和修复方案：

**错误信息**:
{{error_message}}

**复现步骤** (可选):
{{reproduction_steps}}

**相关文件** (可选):
{{file_paths}}

诊断框架：

1. **错误分类**
   - HTTP 4xx：检查 schema 校验（extra="forbid" / Field 约束）、路由路径、NotFoundError
   - HTTP 5xx：检查 db 连接（pool_pre_ping）、未捕获异常、ORM 操作顺序
   - 422 Validation Error：检查请求体字段名/类型是否与 {Resource}Create 一致
   - pytest 失败：检查 conftest.py 的 reset_db autouse fixture 是否正确执行 drop_all + create_all，dependency_overrides 是否生效，class-based 测试是否通过 setup fixture 注入 self.client

2. **项目特有检查点**
   - 错误响应格式：{"success": false, "error": {"code": ..., "message": ..., "path": ...}}
   - 自定义异常需在 app/core/errors.py 定义并继承 HTTPException
   - 测试使用独立数据库（awesome_fastapi_test），通过 TEST_DATABASE_URL 环境变量覆盖

3. **修复建议**
   - 给出最小改动的修复代码
   - 说明根因，避免同类问题再次出现

输出：根因分析 + 修复代码 + 验证方法。
```

## update-skills
```
触发时机：{{trigger}}
# 可选：
# - 引入了新依赖
# - 修改了统一错误处理
# - 升级了框架版本
# - 调整了代码规范
# - 项目结构发生变化

请执行以下步骤：
1. 读取当前项目的关键文件：
   - pyproject.toml（依赖变更）
   - app/main.py（中间件/配置变更）
   - app/models/（模型风格变更）
   - app/schemas/（Schema 风格变更）
   - app/api/（路由风格变更）
   - app/core/errors.py（错误处理变更）
   - tests/（测试风格变更）

2. 与 .claude/skills.md 现有模板对比，检查：
   - 依赖库名称/版本是否需要更新
   - 代码风格示例是否仍然一致
   - 错误处理方式是否有变化
   - 命名规范是否有调整
   - 是否有新增的通用模式需要沉淀为 SKILL

3. 更新 .claude/skills.md 中不一致的部分

4. 同步更新 .claude/project.md 的技术栈和结构说明

5. 输出变更摘要：
   - 修改了哪些 SKILL
   - 原因是什么
   - 是否有建议新增的 SKILL
```