import type {
  ExtensionMessage,
  ExtensionMessageResponse,
  JobInfo,
} from "../types/job";
import { parseBossJobInfo } from "../utils/domParser";

chrome.runtime.onMessage.addListener(
  (
    message: ExtensionMessage,
    _sender,
    sendResponse: (response: ExtensionMessageResponse<JobInfo | null>) => void,
  ) => {
    if (message.type !== "GET_JOB_INFO") {
      return false;
    }

    // 每次请求都重新读取当前页面，避免单页应用切换岗位后使用旧数据。
    sendResponse({
      ok: true,
      data: parseBossJobInfo(),
    });
    return false;
  },
);
