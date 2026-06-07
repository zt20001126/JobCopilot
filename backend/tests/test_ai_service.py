import json

import httpx
import pytest

from app.core.config import get_settings
from app.core.exceptions import AITimeoutError, AIUpstreamError
from app.schemas.greeting import GreetingRequest
from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_ai_service_parses_deepseek_json_response(monkeypatch) -> None:
    response_payload = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "simple_version": "关注 FastAPI 服务开发，想进一步沟通。",
                    "professional_version": "岗位涉及 FastAPI 与数据库维护，想了解当前接口建设重点。",
                    "high_reply_version": "请问 FastAPI 服务目前更关注新功能还是性能优化？",
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

    assert "FastAPI" in result.professional_version


def mock_client_factory(
    monkeypatch,
    handler,
) -> None:
    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def build_client(*args, **kwargs):
        return original_client(transport=transport, timeout=kwargs.get("timeout"))

    monkeypatch.setattr(httpx, "AsyncClient", build_client)


@pytest.mark.asyncio
async def test_ai_service_retries_invalid_output_once(monkeypatch) -> None:
    responses = iter([
        {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "simple_version": "您好，我熟悉 FastAPI。",
                        "professional_version": "专业版",
                        "high_reply_version": "高回复率版",
                    }, ensure_ascii=False),
                },
            }],
        },
        {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "simple_version": "关注 FastAPI 服务开发，想进一步了解岗位重点。",
                        "professional_version": "岗位同时涉及 FastAPI 与数据库维护，想请教团队当前更关注接口性能还是数据治理？",
                        "high_reply_version": "请问 FastAPI 岗位目前主要负责新接口建设，还是已有服务维护？",
                    }, ensure_ascii=False),
                },
            }],
        },
    ])
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json=next(responses))

    settings = get_settings()
    monkeypatch.setattr(settings, "deepseek_api_key", "test-key")
    mock_client_factory(monkeypatch, handler)

    result = await AIService().generate_greeting(
        GreetingRequest(
            position_title="Python 后端工程师",
            job_description="负责 FastAPI 接口和数据库开发维护。",
        ),
    )

    assert call_count == 2
    assert "FastAPI" in result.professional_version


@pytest.mark.asyncio
async def test_ai_service_maps_timeout(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    settings = get_settings()
    monkeypatch.setattr(settings, "deepseek_api_key", "test-key")
    mock_client_factory(monkeypatch, handler)

    with pytest.raises(AITimeoutError):
        await AIService().generate_greeting(
            GreetingRequest(
                position_title="Python 后端工程师",
                job_description="负责 FastAPI 接口和数据库开发维护。",
            ),
        )


@pytest.mark.asyncio
async def test_ai_service_maps_upstream_error(monkeypatch) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "upstream failed"})

    settings = get_settings()
    monkeypatch.setattr(settings, "deepseek_api_key", "test-key")
    mock_client_factory(monkeypatch, handler)

    with pytest.raises(AIUpstreamError):
        await AIService().generate_greeting(
            GreetingRequest(
                position_title="Python 后端工程师",
                job_description="负责 FastAPI 接口和数据库开发维护。",
            ),
        )
