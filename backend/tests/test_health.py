import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_health_check() -> None:
    """健康检查应在不调用外部 AI 服务时返回正常状态。"""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
