class AppError(Exception):
    """可安全返回给客户端的业务异常。"""

    def __init__(
        self,
        message: str,
        *,
        error_code: str,
        status_code: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class AIConfigurationError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "AI 服务尚未正确配置",
            error_code="AI_NOT_CONFIGURED",
            status_code=503,
        )


class AIUpstreamError(AppError):
    def __init__(self, message: str = "AI 服务暂时不可用，请稍后重试") -> None:
        super().__init__(
            message,
            error_code="AI_UPSTREAM_ERROR",
            status_code=502,
        )


class AITimeoutError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "AI 服务响应超时，请稍后重试",
            error_code="AI_TIMEOUT",
            status_code=504,
        )


class AIOutputError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "AI 返回内容不符合要求，请重新生成",
            error_code="AI_OUTPUT_INVALID",
            status_code=502,
        )


class RateLimitError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "请求过于频繁，请稍后重试",
            error_code="RATE_LIMITED",
            status_code=429,
        )


class InputLimitError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "岗位描述长度超过限制",
            error_code="JOB_DESCRIPTION_TOO_LONG",
            status_code=413,
        )
