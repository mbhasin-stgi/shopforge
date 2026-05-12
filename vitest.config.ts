import { fileURLToPath } from "node:url";

import { configDefaults, defineConfig, mergeConfig } from "vitest/config";

import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      root: fileURLToPath(new URL("./", import.meta.url)),
      exclude: [...configDefaults.exclude, "e2e/*"],
      server: {
        deps: {
          // Run Vuetify through Vite's transform pipeline so CSS imports
          // are handled by the CSS plugin instead of Node's module loader.
          inline: ["vuetify"],
        },
      },
      coverage: {
        provider: "v8",
        reportsDirectory: "./coverage",
        reporter: ["text", "lcov"],
      },
      setupFiles: ["./vitest-setup.ts"],
    },
  }),
);
