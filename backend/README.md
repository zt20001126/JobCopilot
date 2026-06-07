# JobCopilot Backend

FastAPI 后端负责参数校验、招呼语生成流程编排、AI 服务调用和生成记录保存。MVP 默认启用 mock 模式，便于插件联调。

## 启动方式

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

服务默认运行在 `http://localhost:8000`。

## 运行测试

```powershell
python -m pytest
```

测试默认不调用 DeepSeek API，当前覆盖基础健康检查接口。

## 环境配置

`.env.example` 提供完整模板：

- `DATABASE_URL`：MVP 默认 `sqlite:///./jobcopilot.db`
- `ENABLE_MOCK_AI`：默认 `true`，无需 API Key 即可联调
- `DEEPSEEK_API_KEY`：真实 AI 调用的服务端密钥
- `DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`：模型服务配置
- `REQUEST_TIMEOUT_SECONDS`：模型请求超时
- `STORE_JOB_DESCRIPTION`：是否保存完整 JD，默认关闭
- `CORS_ORIGINS`、`CORS_ORIGIN_REGEX`：跨域访问控制

真实密钥只应写入本地或部署环境的 `.env`，不要提交到仓库。

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
  "high_reply_version": "高回复率版招呼语"
}
```

交互式接口文档位于 `http://localhost:8000/docs`。
