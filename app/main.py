from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.items import router as items_router
from app.db.session import Base, engine
from app.dependencies.common import AppConfig, get_config
from app.models import Item  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Awesome FastAPI Demo", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path),
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "Validation failed",
                "path": str(request.url.path),
                "details": exc.errors(),
            },
        },
    )


@app.get("/")
def health_check(config: AppConfig = Depends(get_config)) -> dict:
    return {
        "success": True,
        "message": "Service is healthy",
        "app": config.app_name,
        "version": config.version,
    }


app.include_router(items_router)
