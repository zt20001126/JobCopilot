from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.core.exceptions import InputLimitError
from app.schemas.greeting import GreetingRequest, GreetingResponse
from app.services.ai_service import AIService
from app.services.greeting_service import GreetingService
from app.utils.logger import get_logger


router = APIRouter(prefix="/greeting", tags=["greeting"])
logger = get_logger(__name__)


@router.post("/generate", response_model=GreetingResponse)
async def generate_greeting(
    payload: GreetingRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> GreetingResponse:
    """根据岗位 JD 生成三种风格的招呼语。"""
    if len(payload.job_description) > get_settings().max_job_description_length:
        raise InputLimitError()

    service = GreetingService(ai_service=AIService(), db=db)
    logger.info(
        "Greeting generation started",
        extra={"position_title_length": len(payload.position_title)},
    )
    return await service.generate(payload, request.state.request_id)
