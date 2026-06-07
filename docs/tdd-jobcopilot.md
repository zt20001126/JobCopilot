# JobCopilot（AI 求职副驾驶）技术设计文档

| 项目 | 内容 |
| --- | --- |
| 文档类型 | Technical Design Document |
| 当前阶段 | MVP |
| 客户端 | Chrome / Edge 浏览器插件 |
| 服务端 | FastAPI |
| AI 服务 | DeepSeek API |

## 1. 技术目标

构建一个基于 Manifest V3 的浏览器插件，在 Boss直聘岗位详情页提取职位名称与岗位描述，通过后端调用 DeepSeek API，生成 3 条不同风格的招呼语并支持一键复制。

设计需满足：

- AI Key 和服务端规则不暴露给插件。
- 正常网络环境下，生成结果在 10 秒内返回。
- 插件与招聘平台解析逻辑解耦，便于后续支持其他平台。
- 后端模块可扩展至简历分析、岗位匹配和面试预测。

## 2. 系统架构

```text
用户
  ↓
Chrome / Edge Extension
  ├─ Content Script：采集岗位信息
  ├─ Popup：触发生成、展示结果、复制
  └─ Service Worker：消息协调、请求后端
  ↓ HTTPS
FastAPI Backend
  ├─ API 层
  ├─ JD 解析与校验
  ├─ 招呼语生成服务
  ├─ DeepSeek 客户端
  └─ 数据访问层
  ↓
DeepSeek API / SQLite
```

### 2.1 架构职责

| 层级 | 主要职责 |
| --- | --- |
| 浏览器插件 | 页面识别、JD 采集、交互展示、复制 |
| FastAPI | 参数校验、业务编排、AI 调用、结果校验、限流 |
| DeepSeek API | JD 分析与招呼语生成 |
| 数据库 | 保存必要的生成记录和运行指标 |

## 3. 技术选型

| 模块 | 技术 |
| --- | --- |
| 插件语言 | TypeScript |
| 插件 UI | Vue 3 |
| 构建工具 | Vite |
| 插件规范 | Chrome Extension Manifest V3 |
| 后端语言 | Python |
| Web 框架 | FastAPI |
| 数据校验 | Pydantic |
| ORM | SQLAlchemy |
| MVP 数据库 | SQLite |
| 正式环境数据库 | PostgreSQL |
| AI 服务 | DeepSeek API |
| 接口协议 | HTTPS + JSON |

SQLite 与 PostgreSQL 使用统一 ORM 模型和迁移机制，避免业务层依赖数据库方言。

## 4. 插件端设计

### 4.1 模块划分

#### Content Script

- 判断当前页面是否为受支持的岗位详情页。
- 提取职位名称、岗位描述和当前 URL。
- 监听单页应用路由及页面内容变化。
- 将标准化后的岗位信息发送给 Service Worker。

#### 平台适配器

为每个招聘平台定义独立解析器，统一输出：

- `platform`
- `position_title`
- `job_description`
- `job_url`

MVP 仅实现 Boss直聘适配器。DOM 选择器集中维护，不与 UI 或请求逻辑混合。

#### Service Worker

- 协调 Content Script 与 Popup 的消息。
- 调用后端 API。
- 管理请求超时和统一错误转换。
- 仅缓存当前标签页的临时岗位上下文，不长期保存 JD。

#### Popup

- 展示当前职位与识别状态。
- 发起生成请求并防止重复提交。
- 展示简洁版、专业版和高回复率版。
- 提供重新生成、错误重试和一键复制。

### 4.2 权限原则

Manifest 仅申请功能必需权限：

- 当前标签页或明确的 Boss直聘站点访问权限。
- 后端 API 域名访问权限。
- 使用浏览器剪贴板能力完成复制。

不读取账号凭据、聊天记录或其他非岗位页面数据。

## 5. 后端设计

### 5.1 模块划分

| 模块 | 职责 |
| --- | --- |
| API 层 | 路由、请求校验、响应封装 |
| Greeting Service | 生成流程编排和业务规则校验 |
| JD Parser | 清洗 JD，识别技能、职责和要求 |
| Prompt Builder | 构造版本化提示词和输出约束 |
| DeepSeek Client | AI 请求、超时、重试和异常映射 |
| Output Validator | 校验三种风格、字数和内容完整性 |
| Repository | 生成记录读写，与数据库解耦 |

### 5.2 生成流程

1. API 校验职位名称与 JD 长度。
2. 对输入进行去空白、去重复和基础清洗。
3. JD Parser 提取技能关键词、岗位职责和岗位要求。
4. Prompt Builder 生成结构化提示词，要求 AI 返回固定字段。
5. DeepSeek Client 调用模型，并要求结构化 JSON 输出。
6. Output Validator 校验字段、字数和内容质量。
7. 校验失败时允许一次修复或重新生成。
8. 返回统一响应，并按配置记录必要的生成元数据。

### 5.3 AI 输出约束

- 必须返回 `simple`、`professional`、`high_reply` 三个字段。
- 每条招呼语不超过 100 个汉字。
- 三条内容需有明显表达差异。
- 至少关联一个有效岗位要素。
- 不生成未经用户提供的个人经历、学历或成果。
- 不输出解释、Markdown 或额外字段。

提示词需配置版本号，便于质量对比与回滚。

## 6. API 设计

### 6.1 生成招呼语

**接口**

`POST /api/v1/greetings/generate`

**请求体**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `position_title` | string | 是 | 职位名称 |
| `job_description` | string | 是 | 岗位描述 |
| `job_url` | string | 否 | 当前岗位 URL |
| `platform` | string | 否 | 来源平台，MVP 为 `boss` |

**成功响应**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `request_id` | string | 请求追踪标识 |
| `simple_version` | string | 简洁版 |
| `professional_version` | string | 专业版 |
| `high_reply_version` | string | 高回复率版 |
| `generated_at` | datetime | 生成时间 |

**错误约定**

| HTTP 状态 | 场景 |
| --- | --- |
| `400` | JD 缺失、过短或格式无效 |
| `429` | 请求频率超限 |
| `502` | AI 服务调用或结果解析失败 |
| `504` | AI 服务响应超时 |
| `500` | 未预期服务端错误 |

错误响应统一包含 `request_id`、`error_code` 和面向用户的 `message`，不返回内部堆栈或第三方敏感信息。

### 6.2 服务状态

`GET /health`

用于部署健康检查，仅返回服务状态，不执行 DeepSeek 实时调用。

## 7. 数据库设计

### 7.1 generation_record

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | UUID / string | 主键 |
| `request_id` | string | 请求追踪标识，唯一索引 |
| `user_id` | string, nullable | MVP 不登录，预留字段 |
| `platform` | string | 招聘平台 |
| `position_title` | string | 职位名称 |
| `job_url` | string, nullable | 岗位 URL |
| `job_description` | text, nullable | 默认不长期保存，可配置关闭 |
| `generated_content` | JSON / text | 三种生成结果 |
| `prompt_version` | string | 提示词版本 |
| `model_name` | string | AI 模型标识 |
| `status` | string | success / failed |
| `latency_ms` | integer | 生成耗时 |
| `created_at` | datetime | 创建时间 |

### 7.2 数据策略

- MVP 不依赖用户账号，`user_id` 为空。
- 默认优先保存脱敏后的运行元数据；是否保存完整 JD 由隐私策略配置。
- 失败请求不记录 AI Key、完整异常堆栈或敏感请求头。
- 正式版通过数据库迁移工具由 SQLite 切换至 PostgreSQL。

## 8. 安全与隐私

- DeepSeek API Key 仅通过后端环境变量配置。
- 插件与后端只通过 HTTPS 通信。
- 后端设置允许的插件来源和 API 域名，不开放任意跨域访问。
- 对 IP、设备匿名标识或未来用户 ID 实施频率限制。
- 限制 JD 最大长度，防止超大请求和成本滥用。
- 对日志中的 URL、JD 和第三方响应进行脱敏或截断。
- 插件不持久化招聘平台账号、简历或聊天信息。
- 用户复制后自行发送，MVP 不自动操作招聘平台聊天功能。

## 9. 性能与可靠性

- 后端整体请求超时不超过 10 秒。
- DeepSeek 调用设置独立连接和读取超时。
- 仅对超时、限流等可恢复错误进行有限重试，避免重复消耗。
- 同一插件实例生成期间禁止重复提交。
- API 返回 `request_id`，用于前后端日志关联。
- 监控请求量、成功率、P95 延迟、AI 错误率及输出校验失败率。

MVP 不引入消息队列和分布式缓存；达到并发或成本瓶颈后再评估 Redis、异步任务等组件。

## 10. 配置与部署

### 10.1 环境配置

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DATABASE_URL`
- `REQUEST_TIMEOUT`
- `RATE_LIMIT`
- `LOG_LEVEL`
- `STORE_JOB_DESCRIPTION`

### 10.2 部署单元

- 插件：构建 Chrome / Edge 可安装包。
- 后端：容器化部署 FastAPI 服务。
- 数据库：开发及 MVP 使用 SQLite 持久卷；正式环境使用托管 PostgreSQL。
- 环境分为本地、测试、生产，配置与密钥相互隔离。

## 11. 测试方案

| 类型 | 重点 |
| --- | --- |
| 单元测试 | JD 清洗、输出校验、错误映射、平台解析器 |
| 接口测试 | 请求校验、成功响应、限流、超时和 AI 异常 |
| 插件测试 | 页面识别、岗位切换、生成状态、复制功能 |
| 集成测试 | 插件到后端、后端到模拟 AI 服务的完整流程 |
| 兼容性测试 | 主流版本 Chrome 与 Edge |
| 安全测试 | Key 泄漏、CORS、超长输入、频率限制 |

AI 相关自动化测试使用固定模拟响应，避免测试结果受模型波动和外部费用影响；上线前执行少量真实模型质量验证。

## 12. MVP 范围

### 本期实现

- Boss直聘岗位名称、JD 和 URL 提取。
- Chrome / Edge 插件 Popup 交互。
- 后端生成接口与 DeepSeek API 集成。
- 三种招呼语生成、结果校验与一键复制。
- 基础限流、超时、日志和错误处理。

### 本期不实现

- 登录、会员、支付和使用次数系统。
- 简历上传、解析与岗位匹配。
- 自动发送消息或批量投递。
- 批量岗位分析。
- 多招聘平台适配。
- 高可用集群、消息队列和复杂缓存。

## 13. 后续扩展

- **V1**：增加对象存储与简历解析服务，提供岗位匹配度评分。
- **V2**：扩展 AI 任务类型，支持面试问题预测与求职报告。
- **V3**：接入用户、订阅、额度和批量任务系统；增加平台适配器。

现有 API 通过 `/api/v1` 进行版本隔离，新增能力采用独立资源接口，避免破坏 MVP 客户端兼容性。
