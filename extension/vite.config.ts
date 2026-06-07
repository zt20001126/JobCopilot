import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig, loadEnv } from "vite";

const rootDir = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig(({ mode }) => {
  const fileEnv = loadEnv(mode, rootDir, "");
  const apiBaseUrl =
    process.env.VITE_API_BASE_URL ?? fileEnv.VITE_API_BASE_URL;

  if (!apiBaseUrl) {
    throw new Error(
      "缺少 VITE_API_BASE_URL，请先根据 .env.example 创建 .env",
    );
  }

  const apiPermission = `${new URL(apiBaseUrl).origin}/*`;

  return {
    plugins: [
      vue(),
      {
        name: "generate-extension-manifest",
        closeBundle() {
          // 根据环境配置生成后端域名权限，避免在源码中写死接口地址。
          const manifest = JSON.parse(
            readFileSync(resolve(rootDir, "manifest.json"), "utf-8"),
          ) as { host_permissions: string[] };
          // 使用 Set 去重，避免后端域名与已有站点权限重复。
          manifest.host_permissions = Array.from(
            new Set([...manifest.host_permissions, apiPermission]),
          );

          mkdirSync(resolve(rootDir, "dist"), { recursive: true });
          writeFileSync(
            resolve(rootDir, "dist", "manifest.json"),
            `${JSON.stringify(manifest, null, 2)}\n`,
            "utf-8",
          );
        },
      },
    ],
    build: {
      outDir: "dist",
      emptyOutDir: true,
      rollupOptions: {
        input: {
          popup: resolve(rootDir, "src/popup/index.html"),
          sidepanel: resolve(rootDir, "src/sidepanel/index.html"),
          background: resolve(rootDir, "src/background/index.ts"),
          content: resolve(rootDir, "src/content/index.ts"),
        },
        output: {
          // Manifest 直接引用稳定的入口文件名，页面共享依赖仍可拆分到 assets。
          entryFileNames: "[name].js",
          chunkFileNames: "assets/[name]-[hash].js",
          assetFileNames: "assets/[name]-[hash][extname]",
        },
      },
    },
  };
});
