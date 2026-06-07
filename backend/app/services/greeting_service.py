import json
from time import perf_counter

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.generation_record import GenerationRecord
from app.schemas.greeting import GreetingRequest, GreetingResponse
from app.services.ai_service import AIService


class GreetingService:
    """编排招呼语生成流程，并隔离 API 层与 AI 服务实现。"""

    def __init__(self, ai_service: AIService, db: Session) -> None:
        self.ai_service = ai_service
        self.db = db
        self.settings = get_settings()

    async def generate(self, payload: GreetingRequest) -> GreetingResponse:
        started_at = perf_counter()

        if self.settings.enable_mock_ai:
            result = self._build_mock_response(payload.position_title)
        else:
            result = await self.ai_service.generate_greeting(payload)

        latency_ms = int((perf_counter() - started_at) * 1000)
        self._save_record(payload, result, latency_ms)
        return result

    @staticmethod
    def _build_mock_response(position_title: str) -> GreetingResponse:
        """提供可联调的占位结果，不代表最终 AI 生成质量。"""
        return GreetingResponse(
            simple_version=f"您好，我对贵司的{position_title}岗位很感兴趣，希望进一步了解岗位情况。",
            professional_version=f"您好，我关注到贵司正在招聘{position_title}，岗位方向与我的求职目标契合，期待与您进一步沟通。",
            high_reply_version=f"您好，我认真阅读了{position_title}的岗位要求，对相关工作内容很感兴趣，方便聊聊团队和岗位重点吗？",
        )

    def _save_record(
        self,
        payload: GreetingRequest,
        result: GreetingResponse,
        latency_ms: int,
    ) -> None:
        record = GenerationRecord(
            position_title=payload.position_title,
            job_description=(
                payload.job_description
                if self.settings.store_job_description
                else None
            ),
            job_url=str(payload.job_url) if payload.job_url else None,
            generated_content=json.dumps(
                result.model_dump(),
                ensure_ascii=False,
            ),
            latency_ms=latency_ms,
        )
        self.db.add(record)
        self.db.commit()
