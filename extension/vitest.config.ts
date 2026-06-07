import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: "jsdom",
    environmentOptions: {
      // 固定为 Boss 域名，使 URL 安全校验与真实内容脚本环境一致。
      jsdom: {
        url: "https://www.zhipin.com/",
      },
    },
    include: ["tests/**/*.test.ts"],
    clearMocks: true,
  },
});
