import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";

import SidePanel from "../src/sidepanel/App.vue";


const jobInfo = {
  platform: "boss" as const,
  positionTitle: "Python 后端工程师",
  jobDescription: "负责 FastAPI 接口和数据库开发维护。",
  jobUrl: "https://www.zhipin.com/job_detail/example.html",
};

describe("SidePanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("重新生成失败时清空旧结果并提供重试入口", async () => {
    const runtimeSendMessage = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        data: {
          simple_version: "简洁内容",
          professional_version: "专业内容",
          high_reply_version: "高回复内容",
          model_name: "deepseek-v4-flash",
        },
      })
      .mockRejectedValueOnce(new Error("offline"));

    vi.stubGlobal("chrome", {
      tabs: {
        query: vi.fn().mockResolvedValue([{ id: 1 }]),
        sendMessage: vi.fn().mockResolvedValue({ ok: true, data: jobInfo }),
      },
      runtime: {
        sendMessage: runtimeSendMessage,
        onMessage: {
          addListener: vi.fn(),
          removeListener: vi.fn(),
        },
      },
    });

    const wrapper = mount(SidePanel);
    await flushPromises();

    await wrapper.get(".primary-button").trigger("click");
    await flushPromises();
    expect(wrapper.text()).toContain("简洁内容");
    expect(wrapper.text()).toContain("模型：deepseek-v4-flash");

    await wrapper.get(".primary-button").trigger("click");
    await flushPromises();
    expect(wrapper.text()).not.toContain("简洁内容");
    expect(wrapper.text()).toContain("插件通信失败");
    expect(wrapper.get(".primary-button").text()).toBe("重试生成");

    wrapper.unmount();
  });
});
