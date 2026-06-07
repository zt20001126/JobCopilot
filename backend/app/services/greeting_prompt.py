import json

from app.schemas.greeting import GreetingRequest


PROMPT_VERSION = "greeting-v1"

SYSTEM_PROMPT = """你是中文求职沟通助手。根据岗位信息生成三条发给招聘者的首次招呼语。
必须遵守：
1. 只使用岗位信息，不虚构求职者经历、学历、技能或成果。
2. 当前没有提供求职者简历，禁止使用“我有经验、我熟悉、我掌握、我具备、我擅长、我做过、能够胜任”等个人能力陈述。
3. 可以表达对岗位方向的兴趣、指出岗位中的具体技术或职责，并提出自然的沟通问题。
4. 每条不超过100个中文字符，表达自然，避免空泛模板。
5. 三条风格分别为简洁、专业、高回复率，并体现具体岗位要素。
6. 仅返回JSON，不要Markdown、解释或额外字段。
JSON格式示例：
{"simple_version":"内容","professional_version":"内容","high_reply_version":"内容"}"""


def build_greeting_messages(payload: GreetingRequest) -> list[dict[str, str]]:
    """构造版本化 Prompt，用户输入作为 JSON 数据传递以降低提示词注入风险。"""
    job_data = {
        "position_title": payload.position_title,
        "job_description": payload.job_description,
        "platform": payload.platform,
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请根据以下岗位数据生成招呼语：{json.dumps(job_data, ensure_ascii=False)}",
        },
    ]
