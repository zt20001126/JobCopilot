import { afterEach, describe, expect, it } from "vitest";

import { parseBossJobInfo } from "../src/utils/domParser";

describe("parseBossJobInfo", () => {
  afterEach(() => {
    document.body.innerHTML = "";
    window.history.replaceState({}, "", "/");
  });

  it("从候选选择器读取并标准化岗位信息", () => {
    document.body.innerHTML = `
      <h1 data-job-title> Python 后端工程师 </h1>
      <section data-job-description> 负责 FastAPI 服务开发与维护。 </section>
    `;
    window.history.replaceState({}, "", "/job/example");

    expect(parseBossJobInfo()).toEqual({
      platform: "boss",
      positionTitle: "Python 后端工程师",
      jobDescription: "负责 FastAPI 服务开发与维护。",
      jobUrl: "http://localhost:3000/job/example",
    });
  });

  it("缺少岗位标题或描述时返回 null", () => {
    document.body.innerHTML = "<h1 data-job-title>Python 后端工程师</h1>";

    expect(parseBossJobInfo()).toBeNull();
  });
});
