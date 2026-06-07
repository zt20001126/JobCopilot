import pytest

from app.core.exceptions import AIOutputError
from app.services.greeting_validator import validate_greeting_output


def test_validate_greeting_output_accepts_three_distinct_versions() -> None:
    result = validate_greeting_output({
        "simple_version": "您好，关注到贵司 Python 后端岗位，想进一步了解。",
        "professional_version": "您好，该岗位的 FastAPI 与数据库方向很有吸引力，期待沟通岗位重点。",
        "high_reply_version": "您好，看到团队重视接口与数据库建设，想请教目前最优先解决的技术问题是什么？",
    })

    assert result.simple_version.startswith("您好")


def test_validate_greeting_output_rejects_overlong_content() -> None:
    with pytest.raises(AIOutputError):
        validate_greeting_output({
            "simple_version": "很" * 101,
            "professional_version": "专业版",
            "high_reply_version": "高回复率版",
        })


def test_validate_greeting_output_rejects_unverified_experience_claims() -> None:
    with pytest.raises(AIOutputError):
        validate_greeting_output({
            "simple_version": "您好，我熟悉 Spring Boot，希望进一步沟通。",
            "professional_version": "专业版",
            "high_reply_version": "高回复率版",
        })
