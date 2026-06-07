import type { GreetingRequest, GreetingResponse } from "../types/job";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const DEFAULT_TIMEOUT_MS = 10_000;

export class GreetingApiError extends Error {
  constructor(
    message: string,
    public readonly code: "CONFIG" | "TIMEOUT" | "NETWORK" | "HTTP",
    public readonly status?: number,
  ) {
    super(message);
    this.name = "GreetingApiError";
  }
}

function getRequestTimeout(): number {
  const configuredTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS);
  return Number.isFinite(configuredTimeout) && configuredTimeout > 0
    ? configuredTimeout
    : DEFAULT_TIMEOUT_MS;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as {
      detail?: unknown;
      message?: unknown;
      error?: unknown;
      request_id?: unknown;
    };
    const candidates = [payload.message, payload.detail, payload.error];
    const message =
      candidates.find((value): value is string => typeof value === "string") ??
      "";
    const requestId =
      typeof payload.request_id === "string" ? payload.request_id : "";
    return message && requestId
      ? `${message}（请求：${requestId.slice(0, 8)}）`
      : message;
  } catch {
    return "";
  }
}

function isGreetingResponse(value: unknown): value is GreetingResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const response = value as Partial<GreetingResponse>;
  return (
    typeof response.simple_version === "string" &&
    typeof response.professional_version === "string" &&
    typeof response.high_reply_version === "string"
  );
}

/**
 * 调用后端招呼语生成接口，具体 AI 服务由后端负责。
 */
export async function generateGreeting(
  payload: GreetingRequest,
): Promise<GreetingResponse> {
  if (!API_BASE_URL) {
    throw new GreetingApiError(
      "插件尚未配置后端服务地址",
      "CONFIG",
    );
  }

  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(
    () => controller.abort(),
    getRequestTimeout(),
  );

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/greeting/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!response.ok) {
      const serverMessage = await readErrorMessage(response);
      throw new GreetingApiError(
        serverMessage || `后端服务返回错误（HTTP ${response.status}）`,
        "HTTP",
        response.status,
      );
    }

    const responseBody: unknown = await response.json();
    if (!isGreetingResponse(responseBody)) {
      throw new GreetingApiError("后端响应格式无效", "HTTP", response.status);
    }

    return responseBody;
  } catch (error) {
    if (error instanceof GreetingApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new GreetingApiError("请求超时，请稍后重试", "TIMEOUT");
    }
    throw new GreetingApiError(
      "无法连接后端服务，请检查服务是否启动",
      "NETWORK",
    );
  } finally {
    globalThis.clearTimeout(timeoutId);
  }
}
