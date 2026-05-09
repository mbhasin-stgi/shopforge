// Type declaration for eslint-config-prettier (no @types package available).
// This file is included by tsconfig.node.json so eslint.config.ts can import it.
declare module "eslint-config-prettier" {
  import type { Linter } from "eslint";
  const config: Linter.Config;
  export default config;
}
