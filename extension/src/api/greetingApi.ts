import type { GreetingRequest, GreetingResponse } from "../types/job";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

/**
 * 调用后端招呼语生成接口，具体 AI 服务由后端负责。
 */
export async function generateGreeting(
  payload: GreetingRequest,
): Promise<GreetingResponse> {
  if (!API_BASE_URL) {
    throw new Error("未配置 VITE_API_BASE_URL");
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/greeting/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`生成请求失败（HTTP ${response.status}）`);
  }

  return response.json() as Promise<GreetingResponse>;
}
