from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """集中管理环境变量，避免在业务代码中硬编码配置。"""

    app_name: str = "JobCopilot API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./jobcopilot.db"
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    request_timeout_seconds: float = 10.0
    enable_mock_ai: bool = True
    store_job_description: bool = False

    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost",
        "http://127.0.0.1",
    ]
    cors_origin_regex: str | None = r"^chrome-extension://.*$"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """允许通过逗号分隔字符串配置多个来源。"""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
