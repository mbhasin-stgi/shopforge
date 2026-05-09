/**
 * ESLint flat config for ShopForge frontend.
 *
 * Flat config (eslint.config.ts) is the new standard replacing .eslintrc.
 * It uses explicit imports instead of string-based extends.
 */
import tseslint from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import prettier from "eslint-config-prettier";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import pluginVue from "eslint-plugin-vue";
import vueParser from "vue-eslint-parser";
export default [
    // Base TypeScript rules
    {
        files: ["**/*.{ts,tsx,vue}"],
        plugins: {
            "@typescript-eslint": tseslint,
            "simple-import-sort": simpleImportSort,
            vue: pluginVue,
        },
        languageOptions: {
            parser: vueParser,
            parserOptions: {
                parser: tsParser,
                ecmaVersion: "latest",
                sourceType: "module",
            },
        },
        rules: {
            // Import sorting (auto-fixable)
            "simple-import-sort/imports": [
                "error",
                {
                    groups: [
                        // Side effects
                        ["^\\u0000"],
                        // Node builtins
                        ["^node:"],
                        // External packages
                        ["^@?\\w"],
                        // Internal aliases (@/)
                        ["^@/"],
                        // Relative imports
                        ["^\\."],
                    ],
                },
            ],
            "simple-import-sort/exports": "error",
            // TypeScript rules
            "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
            "@typescript-eslint/no-explicit-any": "warn",
            // Vue rules
            "vue/multi-word-component-names": "off", // Allow single-word component names
            "vue/component-api-style": ["error", ["script-setup"]], // Enforce <script setup>
        },
    },
    // Prettier must be last (disables conflicting rules)
    prettier,
];
