from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.greeting import router as greeting_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.middleware import RateLimitMiddleware, RequestContextMiddleware
from app.utils.logger import configure_logging, get_logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """数据库结构由 Alembic 管理，应用启动不再直接修改表结构。"""
    yield


settings = get_settings()
configure_logging()
logger = get_logger(__name__)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(greeting_router, prefix="/api/v1")


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    logger.warning(
        exc.message,
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "error_type": exc.error_code,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "request_id": request_id,
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    _: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "request_id": getattr(request.state, "request_id", "-"),
            "error_code": "VALIDATION_ERROR",
            "message": "请求参数不符合要求",
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unexpected server error",
        extra={
            "request_id": getattr(request.state, "request_id", "-"),
            "status_code": 500,
            "error_type": type(exc).__name__,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "request_id": getattr(request.state, "request_id", "-"),
            "error_code": "INTERNAL_ERROR",
            "message": "服务暂时不可用，请稍后重试",
        },
    )


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """提供不依赖外部 AI 服务的基础健康检查。"""
    return {"status": "ok"}
