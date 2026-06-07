import logging

from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """返回使用统一日志级别的标准日志器。"""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    return logging.getLogger(name)
