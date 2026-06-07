import type {
  ExtensionMessage,
  ExtensionMessageResponse,
  JobPageDiagnostic,
  JobInfo,
} from "../types/job";
import {
  getBossPageDiagnostic,
  parseBossJobInfo,
} from "../utils/domParser";
import { watchPageChanges } from "../utils/pageWatcher";
import {
  ensureEntryButton,
  removeEntryButton,
} from "./entryButton";

let currentJobInfo: JobInfo | null = null;

function isSameJob(left: JobInfo | null, right: JobInfo | null): boolean {
  return (
    left?.jobUrl === right?.jobUrl &&
    left?.positionTitle === right?.positionTitle &&
    left?.jobDescription === right?.jobDescription
  );
}

function openSidePanel(): void {
  void chrome.runtime.sendMessage({ type: "OPEN_SIDE_PANEL" });
}

function refreshPageState(): JobInfo | null {
  const nextJobInfo = parseBossJobInfo();

  if (nextJobInfo) {
    ensureEntryButton(() => {
      // 保持在用户点击事件中发消息，后台可据此打开当前标签页的侧边栏。
      openSidePanel();
    });
  } else {
    removeEntryButton();
  }

  if (!isSameJob(currentJobInfo, nextJobInfo)) {
    currentJobInfo = nextJobInfo;
    // 侧边栏打开时可即时刷新；没有接收方时忽略该通知即可。
    void chrome.runtime
      .sendMessage({ type: "JOB_INFO_UPDATED", payload: nextJobInfo })
      .catch(() => undefined);
  }

  return nextJobInfo;
}

chrome.runtime.onMessage.addListener(
  (
    message: ExtensionMessage,
    _sender,
    sendResponse: (
      response: ExtensionMessageResponse<JobInfo | JobPageDiagnostic | null>,
    ) => void,
  ) => {
    if (message.type === "GET_PAGE_DIAGNOSTIC") {
      sendResponse({
        ok: true,
        data: getBossPageDiagnostic(),
      });
      return false;
    }

    if (message.type !== "GET_JOB_INFO") {
      return false;
    }

    // 主动读取时立即刷新，避免恰好处于防抖窗口而返回上一岗位。
    sendResponse({
      ok: true,
      data: refreshPageState(),
    });
    return false;
  },
);

refreshPageState();
watchPageChanges({ onPageChange: refreshPageState });
