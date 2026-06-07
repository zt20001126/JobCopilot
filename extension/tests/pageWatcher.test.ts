import { afterEach, describe, expect, it, vi } from "vitest";

import { watchPageChanges } from "../src/utils/pageWatcher";

describe("watchPageChanges", () => {
  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = "";
    window.history.replaceState({}, "", "/");
  });

  it("合并高频 DOM 更新并只触发一次回调", async () => {
    vi.useFakeTimers();
    const onPageChange = vi.fn();
    const watcher = watchPageChanges({ onPageChange, debounceMs: 100 });

    document.body.append(document.createElement("div"));
    document.body.append(document.createElement("div"));
    await vi.runAllTimersAsync();

    expect(onPageChange).toHaveBeenCalledTimes(1);
    watcher.stop();
  });

  it("路由切换后触发页面刷新", async () => {
    vi.useFakeTimers();
    const onPageChange = vi.fn();
    const watcher = watchPageChanges({ onPageChange, debounceMs: 100 });

    window.history.pushState({}, "", "/job_detail/next.html");
    await vi.runAllTimersAsync();

    expect(onPageChange).toHaveBeenCalledTimes(1);
    watcher.stop();
  });
});
