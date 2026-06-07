const BUTTON_HOST_ID = "jobcopilot-entry";

/**
 * 注入页面入口按钮；重复调用不会创建多个按钮。
 */
export function ensureEntryButton(onClick: () => void): void {
  if (document.getElementById(BUTTON_HOST_ID)) {
    return;
  }

  const host = document.createElement("div");
  host.id = BUTTON_HOST_ID;
  const shadowRoot = host.attachShadow({ mode: "open" });

  // 使用 Shadow DOM 隔离样式，避免按钮与招聘网站样式互相影响。
  shadowRoot.innerHTML = `
    <style>
      button {
        position: fixed;
        right: 24px;
        bottom: 88px;
        z-index: 2147483647;
        border: 0;
        border-radius: 999px;
        padding: 12px 18px;
        background: #3451b2;
        color: #fff;
        box-shadow: 0 8px 24px rgba(52, 81, 178, 0.28);
        cursor: pointer;
        font: 600 14px/1.2 "Microsoft YaHei", sans-serif;
      }
      button:hover {
        background: #29449c;
      }
      button:focus-visible {
        outline: 3px solid rgba(52, 81, 178, 0.35);
        outline-offset: 3px;
      }
    </style>
    <button type="button" aria-label="打开 JobCopilot 生成招呼语">
      AI 生成招呼语
    </button>
  `;

  shadowRoot.querySelector("button")?.addEventListener("click", onClick);
  document.body.append(host);
}

/**
 * 离开岗位页时移除入口，避免在其他 Boss 页面误显示。
 */
export function removeEntryButton(): void {
  document.getElementById(BUTTON_HOST_ID)?.remove();
}
