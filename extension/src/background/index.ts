import { generateGreeting } from "../api/greetingApi";
import type {
  ExtensionMessage,
  ExtensionMessageResponse,
  GreetingResponse,
} from "../types/job";

chrome.runtime.onInstalled.addListener(() => {
  console.info("JobCopilot extension installed.");
});

chrome.runtime.onMessage.addListener(
  (
    message: ExtensionMessage,
    _sender,
    sendResponse: (
      response: ExtensionMessageResponse<GreetingResponse>,
    ) => void,
  ) => {
    if (message.type !== "GENERATE_GREETING") {
      return false;
    }

    // Service Worker 统一负责后端通信，UI 层只处理展示状态。
    generateGreeting(message.payload)
      .then((data) => sendResponse({ ok: true, data }))
      .catch((error: unknown) => {
        const messageText =
          error instanceof Error ? error.message : "生成请求失败";
        sendResponse({ ok: false, error: messageText });
      });

    return true;
  },
);
