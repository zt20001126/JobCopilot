import { afterEach, describe, expect, it, vi } from "vitest";

const payload = {
  position_title: "Python 后端工程师",
  job_description: "负责 FastAPI 服务开发与维护。",
};

async function loadApiModule() {
  vi.resetModules();
  vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000");
  return import("../src/api/greetingApi");
}

describe("generateGreeting", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("返回后端生成结果", async () => {
    const responseBody = {
      simple_version: "简洁版",
      professional_version: "专业版",
      high_reply_version: "高回复率版",
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(responseBody), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const { generateGreeting } = await loadApiModule();

    await expect(generateGreeting(payload)).resolves.toEqual(responseBody);
  });

  it("保留后端返回的错误提示", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({
          message: "岗位描述无效",
          request_id: "12345678-abcd",
        }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const { generateGreeting } = await loadApiModule();

    await expect(generateGreeting(payload)).rejects.toMatchObject({
      code: "HTTP",
      status: 400,
      message: "岗位描述无效（请求：12345678）",
    });
  });

  it("拒绝字段不完整的后端响应", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ simple_version: "简洁版" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const { generateGreeting } = await loadApiModule();

    await expect(generateGreeting(payload)).rejects.toMatchObject({
      code: "HTTP",
      message: "后端响应格式无效",
    });
  });

  it("请求超时后返回可读错误", async () => {
    vi.stubEnv("VITE_API_TIMEOUT_MS", "5");
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, init?: RequestInit) => {
        return new Promise((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => {
            reject(new DOMException("Aborted", "AbortError"));
          });
        });
      }),
    );
    const { generateGreeting } = await loadApiModule();

    await expect(generateGreeting(payload)).rejects.toMatchObject({
      code: "TIMEOUT",
      message: "请求超时，请稍后重试",
    });
  });

  it("后端离线时返回网络错误", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    const { generateGreeting } = await loadApiModule();

    await expect(generateGreeting(payload)).rejects.toMatchObject({
      code: "NETWORK",
      message: "无法连接后端服务，请检查服务是否启动",
    });
  });
});
