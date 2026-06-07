from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


class GreetingRequest(BaseModel):
    position_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=10, max_length=20_000)
    job_url: HttpUrl | None = None
    platform: str = Field(default="boss", max_length=30)

    @field_validator("position_title", "job_description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        """清理多余空白，避免无效输入消耗模型额度。"""
        return " ".join(value.split())


class GreetingResponse(BaseModel):
    simple_version: str
    professional_version: str
    high_reply_version: str
    request_id: str | None = None
    generated_at: datetime | None = None
    model_name: str | None = None


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str
