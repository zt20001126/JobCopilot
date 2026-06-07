import json

import httpx
import pytest

from app.core.config import get_settings
from app.schemas.greeting import GreetingRequest
from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_ai_service_parses_deepseek_json_response(monkeypatch) -> None:
    response_payload = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "simple_version": "简洁招呼语",
                    "professional_version": "专业招呼语",
                    "high_reply_version": "高回复率招呼语",
                }, ensure_ascii=False),
            },
        }],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key"
        body = json.loads(request.content)
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(200, json=response_payload)

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def build_client(*args, **kwargs):
        return original_client(transport=transport, timeout=kwargs.get("timeout"))

    settings = get_settings()
    monkeypatch.setattr(settings, "deepseek_api_key", "test-key")
    monkeypatch.setattr(httpx, "AsyncClient", build_client)

    result = await AIService().generate_greeting(
        GreetingRequest(
            position_title="Python 后端工程师",
            job_description="负责 FastAPI 接口和数据库开发维护。",
        ),
    )

    assert result.professional_version == "专业招呼语"
