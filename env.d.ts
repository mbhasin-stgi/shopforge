/// <reference types="vite/client" />

/**
 * Declare .vue files as modules so TypeScript understands imports.
 * Without this, `import App from './App.vue'` would be a TS error.
 */
declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare module "eslint-config-prettier" {
  import type { Linter } from "eslint";
  const config: Linter.Config;
  export default config;
}

/**
 * Environment variable types.
 * Vite exposes env vars prefixed with VITE_ on import.meta.env
 */
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_TITLE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
