from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.greeting import GreetingRequest, GreetingResponse
from app.services.ai_service import AIService
from app.services.greeting_service import GreetingService
from app.utils.logger import get_logger


router = APIRouter(prefix="/greeting", tags=["greeting"])
logger = get_logger(__name__)


@router.post("/generate", response_model=GreetingResponse)
async def generate_greeting(
    payload: GreetingRequest,
    db: Session = Depends(get_db),
) -> GreetingResponse:
    """生成三种风格的招呼语；MVP 默认返回 mock 数据。"""
    service = GreetingService(ai_service=AIService(), db=db)

    try:
        return await service.generate(payload)
    except NotImplementedError as exc:
        logger.warning("AI service is not configured: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 服务尚未配置",
        ) from exc
