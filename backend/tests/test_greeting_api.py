from collections.abc import Generator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import get_settings
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.mark.asyncio
async def test_generate_greeting_returns_request_metadata(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "enable_mock_ai", True)
    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/greeting/generate",
                json={
                    "position_title": "Python 后端工程师",
                    "job_description": "负责 FastAPI 接口和数据库开发维护。",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"]
    assert body["generated_at"]
    assert body["model_name"] == "mock"
    assert response.headers["X-Request-ID"] == body["request_id"]


@pytest.mark.asyncio
async def test_generate_greeting_returns_structured_validation_error() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/greeting/generate",
            json={"position_title": "", "job_description": "太短"},
        )

    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_generate_greeting_rejects_configured_input_limit(
    monkeypatch,
) -> None:
    monkeypatch.setattr(get_settings(), "max_job_description_length", 20)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/greeting/generate",
            json={
                "position_title": "Python 后端工程师",
                "job_description": "负责 FastAPI 接口、数据库开发、维护和性能优化工作。",
            },
        )

    assert response.status_code == 413
    body = response.json()
    assert body["error_code"] == "JOB_DESCRIPTION_TOO_LONG"
    assert body["request_id"]
