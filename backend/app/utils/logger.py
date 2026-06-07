import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings


request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


class JsonFormatter(logging.Formatter):
    """将日志输出为结构化 JSON，便于按 request_id 检索。"""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(
                record,
                "request_id",
                request_id_context.get(),
            ),
            "message": record.getMessage(),
        }
        for field in ("status_code", "latency_ms", "error_type"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level.upper())


def get_logger(name: str) -> logging.Logger:
    """返回使用统一日志级别的标准日志器。"""
    return logging.getLogger(name)
