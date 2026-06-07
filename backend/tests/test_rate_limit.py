import httpx
import pytest
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.middleware import RateLimitMiddleware, RequestContextMiddleware


@pytest.mark.asyncio
async def test_rate_limit_returns_structured_429(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_requests", 1)
    monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)

    test_app = FastAPI()

    @test_app.post("/api/v1/greeting/generate")
    async def generate() -> dict[str, bool]:
        return {"ok": True}

    test_app.add_middleware(RateLimitMiddleware)
    test_app.add_middleware(RequestContextMiddleware)
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        first = await client.post("/api/v1/greeting/generate")
        second = await client.post("/api/v1/greeting/generate")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error_code"] == "RATE_LIMITED"
    assert second.headers["X-Request-ID"]
