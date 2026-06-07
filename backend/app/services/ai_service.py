from app.core.config import get_settings
from app.schemas.greeting import GreetingRequest, GreetingResponse


class AIService:
    """封装大模型供应商调用，后续可在此接入 DeepSeek API。"""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_greeting(
        self,
        _: GreetingRequest,
    ) -> GreetingResponse:
        # 真实实现应在后端读取 DEEPSEEK_API_KEY，并处理超时、重试和结构化输出。
        raise NotImplementedError("DeepSeek client is not implemented")
