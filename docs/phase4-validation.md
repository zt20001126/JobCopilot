# JobCopilot 阶段四验收记录

验收日期：2026-06-07

## 1. MVP 主链路

| 环节 | 验收结果 |
| --- | --- |
| Boss 岗位标题与 JD 读取 | 通过真实岗位页面验证 |
| 插件调用 FastAPI | 通过，返回 `request_id` |
| FastAPI 调用 DeepSeek | 通过，日志记录上游 `200 OK` |
| 展示三种招呼语 | 通过 |
| 一键复制 | 通过组件逻辑与人工操作验证 |
| 岗位切换清理旧结果 | 通过自动化测试 |

侧边栏显示 `model_name` 和短 `request_id`，可与后端结构化日志对应。

## 2. 异常场景

| 场景 | 预期行为 | 验证方式 |
| --- | --- | --- |
| 非岗位页或解析失败 | 不展示旧岗位，提示重新读取 | DOM 与组件测试 |
| 后端离线 | 提示检查后端服务 | API 单元测试 |
| 请求超时 | 提示稍后重试 | API 单元测试 |
| AI 上游失败 | 返回结构化 `502` 错误 | 后端单元测试 |
| AI 输出不合格 | 自动修复一次，仍失败则报错 | 后端单元测试 |
| 输入超限 | 返回结构化 `413` 错误 | API 测试 |
| 请求过频 | 返回结构化 `429` 错误 | 中间件测试 |
| 重新生成失败 | 立即清空旧结果并显示重试入口 | Side Panel 组件测试 |

## 3. AI 质量

- 使用模型：`deepseek-v4-flash`
- 三组不同岗位连续实测响应时间：2.26 秒、1.97 秒、2.17 秒
- 输出包含简洁版、专业版和高回复率版
- 每条不超过 100 字
- Prompt 要求引用具体 JD 要素，并禁止虚构求职者经历
- 校验器拦截重复内容、超长内容、技术关键词缺失和未经提供的个人能力声明

## 4. 浏览器兼容

- Chrome：已完成真实 Boss 岗位页主链路验证。
- Edge：已通过独立临时配置加载 Manifest V3 扩展；导航 Boss 页面后 content script 可识别岗位 DOM 并注入“AI 生成招呼语”按钮；扩展 Service Worker 可调用后端和 DeepSeek，返回 3 条结果。
- Side Panel 展示、失败重试和复制逻辑由两类 Chromium 浏览器共用，并通过组件测试。
- 最低 Chromium 版本：114。

Chrome 与 Edge 均使用 `extension/dist` 目录加载未打包扩展。

## 5. 自动化命令

```powershell
cd extension
npm test
npm run type-check
npm run build

cd ..\backend
conda run -n agent python -m pytest
conda run -n agent python -m alembic check
```

自动化测试不读取真实 API Key，也不会调用真实 DeepSeek API。
