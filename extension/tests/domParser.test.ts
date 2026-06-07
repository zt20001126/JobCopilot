import { afterEach, describe, expect, it } from "vitest";

import {
  getBossPageDiagnostic,
  isBossJobDetailUrl,
  parseBossJobInfo,
} from "../src/utils/domParser";

describe("parseBossJobInfo", () => {
  afterEach(() => {
    document.body.innerHTML = "";
    window.history.replaceState({}, "", "/");
  });

  it("从候选选择器读取并标准化岗位信息", () => {
    document.body.innerHTML = `
      <h1 data-job-title> Python 后端工程师 </h1>
      <section data-job-description>
        负责 FastAPI 服务开发
        与维护。
      </section>
    `;
    window.history.replaceState({}, "", "/job_detail/example.html");

    expect(parseBossJobInfo()).toEqual({
      platform: "boss",
      positionTitle: "Python 后端工程师",
      jobDescription: "负责 FastAPI 服务开发 与维护。",
      jobUrl: "https://www.zhipin.com/job_detail/example.html",
    });
  });

  it("缺少岗位标题或描述时返回 null", () => {
    document.body.innerHTML = "<h1 data-job-title>Python 后端工程师</h1>";
    window.history.replaceState({}, "", "/job_detail/example.html");

    expect(parseBossJobInfo()).toBeNull();
  });

  it("非岗位详情页即使存在相似 DOM 也不进行解析", () => {
    document.body.innerHTML = `
      <h1 data-job-title>Python 后端工程师</h1>
      <section data-job-description>岗位描述</section>
    `;
    window.history.replaceState({}, "", "/web/geek/recommend");

    expect(parseBossJobInfo()).toBeNull();
  });

  it("解析岗位列表页右侧内嵌的详情面板", () => {
    document.body.innerHTML = `
      <aside class="job-list">
        <article class="job-card-wrap active">
          <span class="job-name">左侧岗位卡片</span>
        </article>
      </aside>
      <main class="job-detail-container">
        <header>
          <h2 class="job-name">Java 后端工程师</h2>
        </header>
        <section class="job-detail-section">
          <h3>职位描述</h3>
          <div class="job-sec-text">
            负责后端功能开发、接口设计与数据库维护。
          </div>
        </section>
      </main>
    `;
    window.history.replaceState(
      {},
      "",
      "/web/geek/jobs?query=&city=101210200&position=100101",
    );

    expect(parseBossJobInfo()).toEqual({
      platform: "boss",
      positionTitle: "Java 后端工程师",
      jobDescription: "职位描述 负责后端功能开发、接口设计与数据库维护。",
      jobUrl:
        "https://www.zhipin.com/web/geek/jobs?query=&city=101210200&position=100101",
    });
  });

  it("岗位列表页没有右侧详情 DOM 时返回 null", () => {
    document.body.innerHTML = `
      <article class="job-card-wrap active">
        <span class="job-name">左侧岗位卡片</span>
      </article>
    `;
    window.history.replaceState({}, "", "/web/geek/jobs?city=101210200");

    expect(parseBossJobInfo()).toBeNull();
  });

  it("类名变化时从职位描述标题附近兜底读取 JD", () => {
    document.body.innerHTML = `
      <article class="job-card-wrap active">
        <span class="job-name">Java 后端工程师</span>
      </article>
      <main class="unknown-detail-panel">
        <section>
          <h3>职位描述</h3>
          <p>负责后端功能开发、接口设计、测试以及线上系统维护工作。</p>
        </section>
      </main>
    `;
    window.history.replaceState({}, "", "/web/geek/jobs?city=101210200");

    expect(parseBossJobInfo()).toMatchObject({
      positionTitle: "Java 后端工程师",
      jobDescription:
        "职位描述 负责后端功能开发、接口设计、测试以及线上系统维护工作。",
    });
    expect(getBossPageDiagnostic()).toMatchObject({
      urlSupported: true,
      titleFound: true,
      descriptionFound: true,
    });
  });
});

describe("isBossJobDetailUrl", () => {
  it.each([
    "https://www.zhipin.com/job_detail/abc123.html",
    "https://www.zhipin.com/web/geek/job?ka=header-job",
    "https://www.zhipin.com/web/geek/jobs?query=&city=101210200",
  ])("识别支持的岗位 URL：%s", (url) => {
    expect(isBossJobDetailUrl(url)).toBe(true);
  });

  it.each([
    "https://www.zhipin.com/web/geek/recommend",
    "https://example.com/job_detail/abc123.html",
    "not-a-url",
  ])("拒绝非岗位 URL：%s", (url) => {
    expect(isBossJobDetailUrl(url)).toBe(false);
  });
});
