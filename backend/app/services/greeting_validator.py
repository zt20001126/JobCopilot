import re

from pydantic import ValidationError

from app.core.exceptions import AIOutputError
from app.schemas.greeting import GreetingResponse


MAX_GREETING_LENGTH = 100
UNVERIFIED_CLAIM_PATTERN = re.compile(
    r"我(?:有|具备|熟悉|掌握|擅长|拥有|做过|负责过|参与过)"
    r"|我的(?:经验|经历|技能|能力)"
    r"|能够胜任",
)


def validate_greeting_output(payload: object) -> GreetingResponse:
    """校验模型结构、字段完整性和单条字数。"""
    try:
        result = GreetingResponse.model_validate(payload)
    except ValidationError as exc:
        raise AIOutputError() from exc

    values = [
        result.simple_version,
        result.professional_version,
        result.high_reply_version,
    ]
    normalized = [value.strip() for value in values]
    if any(not value or len(value) > MAX_GREETING_LENGTH for value in normalized):
        raise AIOutputError()
    if len(set(normalized)) != len(normalized):
        raise AIOutputError()
    if any(UNVERIFIED_CLAIM_PATTERN.search(value) for value in normalized):
        raise AIOutputError()

    return GreetingResponse(
        simple_version=normalized[0],
        professional_version=normalized[1],
        high_reply_version=normalized[2],
    )
