import json
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.generation_record import GenerationRecord
from app.schemas.greeting import GreetingRequest, GreetingResponse
from app.services.ai_service import AIService
from app.services.greeting_prompt import PROMPT_VERSION
from app.services.greeting_validator import validate_greeting_output


class GreetingService:
    """编排招呼语生成流程，并隔离 API 层与 AI 服务实现。"""

    def __init__(self, ai_service: AIService, db: Session) -> None:
        self.ai_service = ai_service
        self.db = db
        self.settings = get_settings()

    async def generate(
        self,
        payload: GreetingRequest,
        request_id: str | None = None,
    ) -> GreetingResponse:
        started_at = perf_counter()
        resolved_request_id = request_id or str(uuid4())

        try:
            if self.settings.enable_mock_ai:
                result = self._build_mock_response(payload.position_title)
            else:
                result = await self.ai_service.generate_greeting(payload)
        except AppError:
            latency_ms = int((perf_counter() - started_at) * 1000)
            self._save_failure(payload, latency_ms, resolved_request_id)
            raise

        latency_ms = int((perf_counter() - started_at) * 1000)
        response = result.model_copy(
            update={
                "request_id": resolved_request_id,
                "generated_at": datetime.now(timezone.utc),
                "model_name": (
                    "mock"
                    if self.settings.enable_mock_ai
                    else self.settings.deepseek_model
                ),
            },
        )
        self._save_record(payload, response, latency_ms, resolved_request_id)
        return response

    @staticmethod
    def _build_mock_response(position_title: str) -> GreetingResponse:
        """提供可联调的占位结果，不代表最终 AI 生成质量。"""
        return validate_greeting_output({
            "simple_version": f"您好，我对贵司的{position_title}岗位很感兴趣，希望进一步了解岗位情况。",
            "professional_version": f"您好，我关注到贵司正在招聘{position_title}，岗位方向与我的求职目标契合，期待与您进一步沟通。",
            "high_reply_version": f"您好，我认真阅读了{position_title}的岗位要求，对相关工作内容很感兴趣，方便聊聊团队和岗位重点吗？",
        })

    def _save_record(
        self,
        payload: GreetingRequest,
        result: GreetingResponse,
        latency_ms: int,
        request_id: str,
    ) -> None:
        record = GenerationRecord(
            request_id=request_id,
            platform=payload.platform,
            position_title=payload.position_title,
            job_description=(
                payload.job_description
                if self.settings.store_job_description
                else None
            ),
            job_url=str(payload.job_url) if payload.job_url else None,
            generated_content=json.dumps(
                result.model_dump(
                    mode="json",
                    exclude={"request_id", "generated_at", "model_name"},
                ),
                ensure_ascii=False,
            ),
            prompt_version=PROMPT_VERSION,
            model_name=(
                "mock"
                if self.settings.enable_mock_ai
                else self.settings.deepseek_model
            ),
            latency_ms=latency_ms,
        )
        self.db.add(record)
        self.db.commit()

    def _save_failure(
        self,
        payload: GreetingRequest,
        latency_ms: int,
        request_id: str,
    ) -> None:
        """仅保存失败元数据，不持久化完整 JD 或第三方响应。"""
        record = GenerationRecord(
            request_id=request_id,
            platform=payload.platform,
            position_title=payload.position_title,
            job_description=None,
            job_url=str(payload.job_url) if payload.job_url else None,
            generated_content="{}",
            prompt_version=PROMPT_VERSION,
            model_name=self.settings.deepseek_model,
            status="failed",
            latency_ms=latency_ms,
        )
        self.db.add(record)
        self.db.commit()
