import type { JobInfo } from "../types/job";

interface PlatformSelectors {
  positionTitle: string[];
  jobDescription: string[];
}

// 页面选择器统一维护在此处，招聘平台结构变化时只需更新该配置。
const BOSS_SELECTORS: PlatformSelectors = {
  positionTitle: [
    "[data-job-title]",
    ".job-title",
  ],
  jobDescription: [
    "[data-job-description]",
    ".job-detail-section",
  ],
};

function readFirstText(selectors: string[]): string {
  for (const selector of selectors) {
    const element = document.querySelector<HTMLElement>(selector);
    const text = (element?.innerText ?? element?.textContent ?? "").trim();
    if (text) {
      return text;
    }
  }

  return "";
}

/**
 * 从当前 Boss直聘页面提取标准化岗位信息。
 * 当前仅提供基础候选选择器，正式接入前需结合页面结构补充验证。
 */
export function parseBossJobInfo(): JobInfo | null {
  const positionTitle = readFirstText(BOSS_SELECTORS.positionTitle);
  const jobDescription = readFirstText(BOSS_SELECTORS.jobDescription);

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
