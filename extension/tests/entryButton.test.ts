import { afterEach, describe, expect, it, vi } from "vitest";

import {
  ensureEntryButton,
  removeEntryButton,
} from "../src/content/entryButton";

describe("entryButton", () => {
  afterEach(() => {
    removeEntryButton();
  });

  it("重复调用时只注入一个入口按钮", () => {
    ensureEntryButton(vi.fn());
    ensureEntryButton(vi.fn());

    expect(document.querySelectorAll("#jobcopilot-entry")).toHaveLength(1);
  });

  it("点击按钮时执行打开侧边栏回调", () => {
    const onClick = vi.fn();
    ensureEntryButton(onClick);

    const host = document.getElementById("jobcopilot-entry");
    const button = host?.shadowRoot?.querySelector("button");
    button?.dispatchEvent(new MouseEvent("click", { bubbles: true }));

    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
