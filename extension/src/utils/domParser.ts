import type { JobInfo, JobPageDiagnostic } from "../types/job";

interface PlatformSelectors {
  positionTitle: string[];
  jobDescription: string[];
}

// Boss 页面选择器统一维护在此处，页面结构变化时只需更新这一份配置。
const BOSS_SELECTORS: PlatformSelectors = {
  positionTitle: [
    "[data-job-title]",
    ".job-detail-container .job-name",
    ".job-detail-container .job-title",
    ".job-detail-container h1",
    ".job-detail-content .job-name",
    ".job-detail-content .job-title",
    ".job-detail-box .job-name",
    ".job-detail-box .job-title",
    ".job-detail-info .job-name",
    ".job-detail-info .name",
    ".job-primary .name h1",
    ".job-primary .name",
    ".job-detail-header .job-name",
    ".job-detail-container h2",
    ".job-detail-box h2",
    ".job-detail-content h2",
    ".job-card-wrap.active .job-name",
    ".job-card-box.active .job-name",
    "[class*='job-card'][class*='active'] [class*='job-name']",
  ],
  jobDescription: [
    "[data-job-description]",
    ".job-detail-container .job-detail-section",
    ".job-detail-container .job-sec-text",
    ".job-detail-content .job-detail-section",
    ".job-detail-content .job-sec-text",
    ".job-detail-box .job-detail-section",
    ".job-detail-box .job-sec-text",
    ".job-detail-section .job-sec-text",
    ".job-detail .job-sec-text",
    ".job-detail .text",
    ".job-detail-section",
  ],
};

const BOSS_HOSTS = new Set(["www.zhipin.com"]);
const BOSS_JOB_PATHS = [
  /^\/job_detail\/[^/]+\.html$/i,
  /^\/web\/geek\/job(?:\/|$)/i,
  // Boss 新版在岗位列表页右侧内嵌岗位详情，URL 不再切换到独立详情路径。
  /^\/web\/geek\/jobs(?:\/|$)/i,
];

function normalizeText(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function readFirstText(selectors: string[]): string {
  for (const selector of selectors) {
    const element = document.querySelector<HTMLElement>(selector);
    const text = normalizeText(
      element?.innerText ?? element?.textContent ?? "",
    );
    if (text) {
      return text;
    }
  }

  return "";
}

function readSemanticDescription(): string {
  const headingCandidates = document.querySelectorAll<HTMLElement>(
    "h1, h2, h3, h4, h5, h6, div, span, p",
  );

  for (const heading of headingCandidates) {
    if (normalizeText(heading.innerText ?? heading.textContent ?? "") !== "职位描述") {
      continue;
    }

    // Boss 页面类名可能变化，兜底读取“职位描述”标题所在的最小内容区块。
    let container = heading.parentElement;
    for (let depth = 0; container && depth < 4; depth += 1) {
      const text = normalizeText(container.innerText ?? container.textContent ?? "");
      if (text.length >= 30 && text.length <= 10_000) {
        return text;
      }
      container = container.parentElement;
    }
  }

  return "";
}

function readJobFields(): Pick<JobInfo, "positionTitle" | "jobDescription"> {
  return {
    positionTitle: readFirstText(BOSS_SELECTORS.positionTitle),
    jobDescription:
      readFirstText(BOSS_SELECTORS.jobDescription) || readSemanticDescription(),
  };
}

/**
 * 判断 URL 是否属于 Boss直聘岗位详情页。
 * URL 规则与 DOM 规则分开维护，避免在其他模块散落平台判断。
 */
export function isBossJobDetailUrl(url: string): boolean {
  try {
    const parsedUrl = new URL(url);
    return (
      BOSS_HOSTS.has(parsedUrl.hostname) &&
      BOSS_JOB_PATHS.some((pattern) => pattern.test(parsedUrl.pathname))
    );
  } catch {
    return false;
  }
}

/**
 * 从当前 Boss直聘页面提取标准化岗位信息。
 * 只有 URL 与核心 DOM 同时满足条件时才返回结果，降低误识别概率。
 */
export function parseBossJobInfo(): JobInfo | null {
  if (!isBossJobDetailUrl(window.location.href)) {
    return null;
  }

  const { positionTitle, jobDescription } = readJobFields();

  if (!positionTitle || !jobDescription) {
    return null;
  }

  return {
    platform: "boss",
    positionTitle,
    jobDescription,
    jobUrl: window.location.href,
  };
}

/** 返回可直接展示在插件弹窗中的页面识别诊断，不包含完整 JD。 */
export function getBossPageDiagnostic(): JobPageDiagnostic {
  const { positionTitle, jobDescription } = readJobFields();

  return {
    pageUrl: window.location.href,
    urlSupported: isBossJobDetailUrl(window.location.href),
    titleFound: Boolean(positionTitle),
    descriptionFound: Boolean(jobDescription),
  };
}
