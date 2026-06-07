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
    sendResponse: (response: ExtensionMessageResponse<GreetingResponse>) => void,
  ) => {
    if (message.type === "OPEN_SIDE_PANEL") {
      const tabId = _sender.tab?.id;
      if (tabId) {
        // sidePanel.open 必须由用户操作触发，因此通过按钮点击消息立即执行。
        void chrome.sidePanel.open({ tabId }).catch((error: unknown) => {
          console.warn("JobCopilot side panel open failed.", error);
        });
      }
      return false;
    }

    if (message.type === "GENERATE_GREETING") {
      // Service Worker 统一负责后端通信，UI 层只处理展示状态。
      generateGreeting(message.payload)
        .then((data) => sendResponse({ ok: true, data }))
        .catch((error: unknown) => {
          const messageText =
            error instanceof Error ? error.message : "生成请求失败";
          sendResponse({ ok: false, error: messageText });
        });

      return true;
    }

    return false;
  },
);
