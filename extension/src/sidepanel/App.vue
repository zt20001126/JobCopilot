<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import type {
  ExtensionMessageResponse,
  GreetingResponse,
  JobInfo,
} from "../types/job";

const jobInfo = ref<JobInfo | null>(null);
const result = ref<GreetingResponse | null>(null);
const loading = ref(false);
const errorMessage = ref("");
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
  errorMessage.value = "";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab.id) {
    errorMessage.value = "未找到当前标签页";
    return;
  }

  try {
    const response = await chrome.tabs.sendMessage<
      { type: "GET_JOB_INFO" },
      ExtensionMessageResponse<JobInfo | null>
    >(tab.id, { type: "GET_JOB_INFO" });
    jobInfo.value = response.data ?? null;

    if (!jobInfo.value) {
      errorMessage.value = "暂未识别到岗位信息，请打开 Boss直聘岗位详情页";
    }
  } catch {
    errorMessage.value = "当前页面未加载 JobCopilot 内容脚本";
  }
}

async function generate(): Promise<void> {
  if (!jobInfo.value || loading.value) {
    return;
  }

  loading.value = true;
  errorMessage.value = "";

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

  loading.value = false;
  if (!response.ok || !response.data) {
    errorMessage.value = response.error ?? "生成失败，请稍后重试";
    return;
  }

  result.value = response.data;
}

async function copyGreeting(key: string, content: string): Promise<void> {
  await navigator.clipboard.writeText(content);
  copiedKey.value = key;
  window.setTimeout(() => {
    copiedKey.value = "";
  }, 1200);
}

onMounted(loadJobInfo);
</script>

<template>
  <main class="panel">
    <header>
      <p class="eyebrow">AI 求职副驾驶</p>
      <h1>JobCopilot</h1>
    </header>

    <section class="job-card">
      <span>当前岗位</span>
      <strong>{{ jobInfo?.positionTitle || "等待识别" }}</strong>
      <button class="link-button" type="button" @click="loadJobInfo">
        重新读取
      </button>
    </section>

    <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>

    <button
      class="primary-button"
      type="button"
      :disabled="!jobInfo || loading"
      @click="generate"
    >
      {{ loading ? "正在生成..." : "AI 生成招呼语" }}
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
