import json

import httpx

from app.core.config import get_settings
from app.core.exceptions import (
    AIConfigurationError,
    AIOutputError,
    AITimeoutError,
    AIUpstreamError,
)
from app.schemas.greeting import GreetingRequest, GreetingResponse
from app.services.greeting_prompt import build_greeting_messages
from app.services.greeting_validator import validate_greeting_output


class AIService:
    """通过 DeepSeek OpenAI 兼容接口生成结构化招呼语。"""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_greeting(
        self,
        payload: GreetingRequest,
    ) -> GreetingResponse:
        if not self.settings.deepseek_api_key:
            raise AIConfigurationError()

        endpoint = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        messages = build_greeting_messages(payload)

        async with httpx.AsyncClient(
            timeout=self.settings.request_timeout_seconds,
        ) as client:
            for attempt in range(2):
                request_body = {
                    "model": self.settings.deepseek_model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "thinking": {"type": "disabled"},
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 500,
                }
                try:
                    response = await client.post(
                        endpoint,
                        headers={
                            "Authorization": (
                                f"Bearer {self.settings.deepseek_api_key}"
                            ),
                            "Content-Type": "application/json",
                        },
                        json=request_body,
                    )
                    response.raise_for_status()
                except httpx.TimeoutException as exc:
                    raise AITimeoutError() from exc
                except httpx.HTTPStatusError as exc:
                    # 不向客户端透传上游响应，避免泄露供应商细节或敏感内容。
                    raise AIUpstreamError() from exc
                except httpx.HTTPError as exc:
                    raise AIUpstreamError() from exc

                try:
                    response_body = response.json()
                    content = response_body["choices"][0]["message"]["content"]
                    model_payload = json.loads(content)
                    return validate_greeting_output(model_payload)
                except (
                    KeyError,
                    IndexError,
                    TypeError,
                    ValueError,
                    json.JSONDecodeError,
                    AIOutputError,
                ) as exc:
                    if attempt == 1:
                        raise AIOutputError() from exc
                    messages.append({
                        "role": "system",
                        "content": (
                            "上次输出不符合格式或包含未经提供的个人经历。"
                            "请严格按原规则重新生成，仅返回合法JSON。"
                        ),
                    })

        raise AIOutputError()
