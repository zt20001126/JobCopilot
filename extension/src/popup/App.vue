<script setup lang="ts">
import { onMounted, ref } from "vue";
import type {
  ExtensionMessageResponse,
  JobInfo,
  JobPageDiagnostic,
} from "../types/job";

const supported = ref(false);
const checking = ref(true);
const statusText = ref("正在检查当前页面...");
const diagnosticText = ref("");
const extensionVersion = chrome.runtime.getManifest().version;

async function checkCurrentPage(): Promise<void> {
  checking.value = true;

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    if (!tab.id) {
      throw new Error("missing tab");
    }

    const response = await chrome.tabs.sendMessage<
      { type: "GET_JOB_INFO" },
      ExtensionMessageResponse<JobInfo | null>
    >(tab.id, { type: "GET_JOB_INFO" });
    supported.value = Boolean(response.data);
    statusText.value = response.data
      ? `已识别：${response.data.positionTitle}`
      : "请打开 Boss直聘岗位详情页";

    if (!response.data) {
      const diagnosticResponse = await chrome.tabs.sendMessage<
        { type: "GET_PAGE_DIAGNOSTIC" },
        ExtensionMessageResponse<JobPageDiagnostic>
      >(tab.id, { type: "GET_PAGE_DIAGNOSTIC" });
      const diagnostic = diagnosticResponse.data;
      if (diagnostic) {
        diagnosticText.value = [
          `URL：${diagnostic.urlSupported ? "已匹配" : "未匹配"}`,
          `标题：${diagnostic.titleFound ? "已找到" : "未找到"}`,
          `JD：${diagnostic.descriptionFound ? "已找到" : "未找到"}`,
        ].join(" · ");
      }
    }
  } catch {
    supported.value = false;
    statusText.value = "插件脚本未连接，请刷新 Boss 页面";
    diagnosticText.value = "若刚重新加载插件，必须同时刷新当前网页";
  } finally {
    checking.value = false;
  }
}

async function openSidePanel(): Promise<void> {
  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    if (!tab.id) {
      throw new Error("missing tab");
    }

    // Popup 按钮属于明确的用户操作，可直接打开当前标签页侧边栏。
    await chrome.sidePanel.open({ tabId: tab.id });
    window.close();
  } catch {
    statusText.value = "侧边栏打开失败，请重新加载插件";
  }
}

onMounted(checkCurrentPage);
</script>

<template>
  <main class="popup">
    <span class="badge">MVP</span>
    <span class="version">v{{ extensionVersion }}</span>
    <h1>JobCopilot</h1>
    <p>AI 求职副驾驶</p>
    <p class="description">
      在 Boss直聘岗位详情页中读取 JD，并生成针对性的求职招呼语。
    </p>
    <p :class="['status', { supported }]">{{ statusText }}</p>
    <p v-if="diagnosticText" class="diagnostic">{{ diagnosticText }}</p>
    <button
      type="button"
      :disabled="checking || !supported"
      @click="openSidePanel"
    >
      打开生成面板
    </button>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  background: #f7f8fc;
  color: #182033;
  font-family: Inter, "Microsoft YaHei", sans-serif;
}

.popup {
  box-sizing: border-box;
  width: 320px;
  padding: 22px;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 999px;
  background: #e8edff;
  color: #3451b2;
  font-size: 12px;
}

.version {
  float: right;
  color: #8a93a8;
  font-size: 12px;
}

h1 {
  margin: 12px 0 4px;
  font-size: 24px;
}

p {
  margin: 0;
  color: #566079;
}

.description {
  margin-top: 16px;
  line-height: 1.6;
}

.status {
  margin-top: 14px;
  border-radius: 8px;
  background: #fff0f0;
  color: #a63131;
  padding: 9px 10px;
  font-size: 13px;
}

.status.supported {
  background: #edf8f0;
  color: #287a42;
}

.diagnostic {
  margin-top: 8px;
  color: #6b7489;
  font-size: 12px;
  line-height: 1.5;
}

button {
  width: 100%;
  margin-top: 14px;
  border: 0;
  border-radius: 9px;
  background: #3451b2;
  color: #fff;
  cursor: pointer;
  padding: 11px 14px;
  font: 600 14px "Microsoft YaHei", sans-serif;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
