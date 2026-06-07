import json

from app.schemas.greeting import GreetingRequest


PROMPT_VERSION = "greeting-v2"

SYSTEM_PROMPT = """你是中文求职沟通助手。根据岗位信息生成三条发给招聘者的首次招呼语。
必须遵守：
1. 只使用岗位信息，不虚构求职者经历、学历、技能或成果。
2. 当前没有提供求职者简历，禁止使用“我有经验、我熟悉、我掌握、我具备、我擅长、我做过、能够胜任”等个人能力陈述。
3. 每条至少引用一个岗位中的具体技术、业务、职责或要求，禁止只替换职位名称。
4. 简洁版控制在35至60字：点明一个岗位重点，并表达沟通意愿。
5. 专业版控制在55至95字：结合两个岗位要素，提出一个有技术或业务含量的问题。
6. 高回复率版控制在45至80字：只问一个招聘者容易快速回答的具体问题。
7. 三条开头和句式应有明显差异，避免重复“我对该岗位很感兴趣”。
8. 仅返回JSON，不要Markdown、解释或额外字段。
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
