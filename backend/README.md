# JobCopilot Backend

FastAPI 后端负责参数校验、招呼语生成流程编排、DeepSeek 调用和生成记录保存。

## 启动方式

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

服务默认运行在 `http://localhost:8000`。

## 运行测试

```powershell
python -m pytest
```

测试使用模拟 AI 响应，不消耗 DeepSeek API 额度。

## 环境配置

`.env.example` 提供完整模板：

- `DATABASE_URL`：MVP 默认 `sqlite:///./jobcopilot.db`
- `ENABLE_MOCK_AI`：默认 `true`，无需 API Key 即可联调
- `DEEPSEEK_API_KEY`：真实 AI 调用的服务端密钥，仅保存在后端
- `DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`：模型服务配置
- `REQUEST_TIMEOUT_SECONDS`：模型请求超时
- `RATE_LIMIT_REQUESTS`、`RATE_LIMIT_WINDOW_SECONDS`：单实例接口限流
- `MAX_JOB_DESCRIPTION_LENGTH`：允许的 JD 最大长度
- `STORE_JOB_DESCRIPTION`：是否保存完整 JD，默认关闭
- `CORS_ORIGINS`、`CORS_ORIGIN_REGEX`：跨域访问控制

真实密钥只应写入本地或部署环境的 `.env`，不要提交到仓库。

启用真实模型：

```dotenv
ENABLE_MOCK_AI=false
DEEPSEEK_API_KEY=你的密钥
DEEPSEEK_MODEL=deepseek-v4-flash
```

修改配置后需要重启后端。数据库变更通过 `python -m alembic upgrade head` 执行。

## API 示例

### 健康检查

```powershell
Invoke-RestMethod http://localhost:8000/health
```

### 生成招呼语

```powershell
$body = @{
  position_title = "Python 后端工程师"
  job_description = "负责 FastAPI 服务开发、数据库设计与接口维护，要求熟悉 Python 和 SQL。"
  job_url = "https://www.zhipin.com/job/example"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/greeting/generate `
  -ContentType "application/json" `
  -Body $body
```

响应字段：

```json
{
  "simple_version": "简洁版招呼语",
  "professional_version": "专业版招呼语",
  "high_reply_version": "高回复率版招呼语",
  "request_id": "请求标识",
  "generated_at": "生成时间"
}
```

交互式接口文档位于 `http://localhost:8000/docs`。
