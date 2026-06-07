# JobCopilot

JobCopilot（AI 求职副驾驶）是一个浏览器插件项目。MVP 面向 Boss直聘岗位详情页，提供岗位信息读取、AI 招呼语生成和一键复制能力。

当前已完成插件 MVP 与 DeepSeek V4 后端接入。

## 技术栈

- 插件端：TypeScript、Vue 3、Vite、Chrome Extension Manifest V3
- 后端：Python、FastAPI、SQLAlchemy、SQLite
- AI 服务：DeepSeek API

## 项目结构

```text
JobCopilot/
├── docs/                         # PRD、TDD、TODO、隐私与验收记录
├── extension/
│   ├── manifest.json             # Manifest V3 配置
│   ├── tests/                    # 插件端自动化测试
│   ├── src/
│   │   ├── api/                  # 后端 API 封装
│   │   ├── background/           # Service Worker
│   │   ├── content/              # 页面内容脚本
│   │   ├── popup/                # 插件弹窗
│   │   ├── sidepanel/            # 招呼语侧边栏
│   │   ├── types/                # TypeScript 类型
│   │   └── utils/                # DOM 解析工具
│   └── vite.config.ts
└── backend/
    ├── app/
    │   ├── api/                  # FastAPI 路由
    │   ├── core/                 # 配置与数据库
    │   ├── models/               # SQLAlchemy 模型
    │   ├── schemas/              # 请求与响应模型
    │   ├── services/             # 业务与 AI 服务
    │   └── utils/                # 通用工具
    ├── tests/                    # 后端 API 测试
    ├── requirements.txt
    ├── requirements-dev.txt
    └── .env.example
```

## 启动插件端

需要 Node.js 20.19+。

```powershell
cd extension
Copy-Item .env.example .env
npm install
npm run build
```

构建完成后：

1. 打开 Chrome 或 Edge 的扩展管理页面。
2. 开启“开发者模式”。
3. 选择“加载已解压的扩展程序”。
4. 选择 `extension/dist` 目录。

开发期间可使用 `npm run dev` 监听文件变化。代码变化后需在扩展管理页重新加载插件。

## 启动后端

需要 Python 3.11+。

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

启动后可访问：

- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`
- 生成接口：`POST http://localhost:8000/api/v1/greeting/generate`

更多后端说明见 [backend/README.md](backend/README.md)。

隐私边界见 [docs/privacy-jobcopilot.md](docs/privacy-jobcopilot.md)，阶段四验证记录见 [docs/phase4-validation.md](docs/phase4-validation.md)。

## 运行测试

插件端：

```powershell
cd extension
npm install
npm test
```

后端：

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest
```

## 环境变量

### 插件端

| 变量 | 说明 |
| --- | --- |
| `VITE_API_BASE_URL` | 后端 API 地址，本地默认 `http://localhost:8000` |
| `VITE_API_TIMEOUT_MS` | 插件请求超时时间，默认 `10000` 毫秒 |

### 后端

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | 数据库连接地址 |
| `ENABLE_MOCK_AI` | 是否返回 mock 招呼语 |
| `DEEPSEEK_API_KEY` | DeepSeek API Key，仅保存在后端 |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 |
| `DEEPSEEK_MODEL` | 使用的模型名称 |
| `REQUEST_TIMEOUT_SECONDS` | 外部 AI 请求超时时间 |
| `MAX_JOB_DESCRIPTION_LENGTH` | JD 最大允许长度 |
| `RATE_LIMIT_REQUESTS` | 限流窗口内允许的请求数 |
| `RATE_LIMIT_WINDOW_SECONDS` | 限流窗口秒数 |
| `STORE_JOB_DESCRIPTION` | 是否保存完整 JD，默认关闭 |
| `CORS_ORIGINS` | 允许的普通 Web 来源 |
| `CORS_ORIGIN_REGEX` | 允许的浏览器插件来源规则 |

请从 `.env.example` 创建本地 `.env`，不要提交真实密钥。

## 当前限制

- MVP 限流基于单进程内存，多实例部署时需改为 Redis。
- 暂未实现登录、简历分析、批量任务和多平台适配。
