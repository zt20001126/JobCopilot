<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import type {
  ExtensionMessage,
  ExtensionMessageResponse,
  GreetingResponse,
  JobInfo,
} from "../types/job";

const jobInfo = ref<JobInfo | null>(null);
const result = ref<GreetingResponse | null>(null);
const readingJob = ref(false);
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const copiedKey = ref("");

const greetingItems = computed(() => {
  if (!result.value) {
    return [];
  }

  return [
    { key: "simple", label: "简洁版", content: result.value.simple_version },
    {
      key: "professional",
      label: "专业版",
      content: result.value.professional_version,
    },
    {
      key: "highReply",
      label: "高回复率版",
      content: result.value.high_reply_version,
    },
  ];
});

async function loadJobInfo(): Promise<void> {
  readingJob.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    if (!tab.id) {
      errorMessage.value = "未找到当前标签页";
      jobInfo.value = null;
      result.value = null;
      return;
    }

    const response = await chrome.tabs.sendMessage<
      { type: "GET_JOB_INFO" },
      ExtensionMessageResponse<JobInfo | null>
    >(tab.id, { type: "GET_JOB_INFO" });
    jobInfo.value = response.data ?? null;

    if (!jobInfo.value) {
      result.value = null;
      errorMessage.value = "暂未识别到岗位信息，请打开 Boss直聘岗位详情页";
    }
  } catch {
    jobInfo.value = null;
    result.value = null;
    errorMessage.value = "当前页面未加载 JobCopilot 内容脚本";
  } finally {
    readingJob.value = false;
  }
}

async function generate(): Promise<void> {
  if (!jobInfo.value || loading.value) {
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const response = await chrome.runtime.sendMessage<
      {
        type: "GENERATE_GREETING";
        payload: {
          position_title: string;
          job_description: string;
          job_url: string;
        };
      },
      ExtensionMessageResponse<GreetingResponse>
    >({
      type: "GENERATE_GREETING",
      payload: {
        position_title: jobInfo.value.positionTitle,
        job_description: jobInfo.value.jobDescription,
        job_url: jobInfo.value.jobUrl,
      },
    });

    if (!response?.ok || !response.data) {
      errorMessage.value = response?.error ?? "生成失败，请稍后重试";
      return;
    }

    result.value = response.data;
    successMessage.value = "已生成 3 条招呼语";
  } catch {
    errorMessage.value = "插件通信失败，请重新加载插件后重试";
  } finally {
    loading.value = false;
  }
}

async function copyGreeting(key: string, content: string): Promise<void> {
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await navigator.clipboard.writeText(content);
    copiedKey.value = key;
    successMessage.value = "招呼语已复制";
    window.setTimeout(() => {
      copiedKey.value = "";
      successMessage.value = "";
    }, 1200);
  } catch {
    errorMessage.value = "复制失败，请检查浏览器剪贴板权限";
  }
}

function handleJobInfoUpdated(message: ExtensionMessage): void {
  if (message.type !== "JOB_INFO_UPDATED") {
    return;
  }

  const hasJobChanged =
    jobInfo.value?.jobUrl !== message.payload?.jobUrl ||
    jobInfo.value?.positionTitle !== message.payload?.positionTitle ||
    jobInfo.value?.jobDescription !== message.payload?.jobDescription;
  jobInfo.value = message.payload;
  errorMessage.value = message.payload
    ? ""
    : "当前页面不是可识别的 Boss直聘岗位详情页";

  if (hasJobChanged) {
    // 岗位切换后清空旧结果，防止用户误复制上一岗位内容。
    result.value = null;
    successMessage.value = "";
  }
}

onMounted(() => {
  chrome.runtime.onMessage.addListener(handleJobInfoUpdated);
  void loadJobInfo();
});

onUnmounted(() => {
  chrome.runtime.onMessage.removeListener(handleJobInfoUpdated);
});
</script>

<template>
  <main class="panel">
    <header>
      <p class="eyebrow">AI 求职副驾驶</p>
      <h1>JobCopilot</h1>
    </header>

    <section class="job-card">
      <span>当前岗位</span>
      <strong>
        {{ jobInfo?.positionTitle || (readingJob ? "正在识别..." : "等待识别") }}
      </strong>
      <button
        class="link-button"
        type="button"
        :disabled="readingJob"
        @click="loadJobInfo"
      >
        {{ readingJob ? "读取中..." : "重新读取" }}
      </button>
    </section>

    <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="message success">{{ successMessage }}</p>

    <button
      class="primary-button"
      type="button"
      :disabled="!jobInfo || loading"
      @click="generate"
    >
      {{ loading ? "正在生成..." : result ? "重新生成" : "AI 生成招呼语" }}
    </button>

    <section class="results" aria-live="polite">
      <article v-for="item in greetingItems" :key="item.key" class="result-card">
        <h2>{{ item.label }}</h2>
        <p>{{ item.content }}</p>
        <button
          class="copy-button"
          type="button"
          @click="copyGreeting(item.key, item.content)"
        >
          {{ copiedKey === item.key ? "已复制" : "复制" }}
        </button>
      </article>

      <p v-if="!result && !loading" class="empty">
        生成结果将在这里展示。
      </p>
    </section>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  background: #f7f8fc;
  color: #182033;
  font-family: Inter, "Microsoft YaHei", sans-serif;
}

button {
  font: inherit;
}

.panel {
  box-sizing: border-box;
  min-height: 100vh;
  padding: 24px 18px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #5269c7;
  font-size: 13px;
  font-weight: 600;
}

h1 {
  margin: 0 0 20px;
  font-size: 26px;
}

.job-card,
.result-card {
  border: 1px solid #e2e5ef;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
}

.job-card span,
.job-card strong {
  display: block;
}

.job-card span {
  color: #707890;
  font-size: 12px;
}

.job-card strong {
  margin-top: 5px;
}

.link-button,
.copy-button {
  border: 0;
  background: transparent;
  color: #3451b2;
  cursor: pointer;
}

.link-button {
  margin-top: 10px;
  padding: 0;
}

.primary-button {
  width: 100%;
  margin-top: 14px;
  border: 0;
  border-radius: 10px;
  background: #3451b2;
  color: #fff;
  cursor: pointer;
  padding: 12px 16px;
  font-weight: 600;
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.message {
  margin: 12px 0 0;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
}

.error {
  background: #fff0f0;
  color: #a63131;
}

.success {
  background: #edf8f0;
  color: #287a42;
}

.results {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.result-card h2 {
  margin: 0;
  font-size: 15px;
}

.result-card p {
  margin: 9px 0;
  color: #4f586f;
  line-height: 1.6;
}

.copy-button {
  padding: 0;
}

.empty {
  color: #7c8498;
  text-align: center;
}
</style>
