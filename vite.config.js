/**
 * Vite configuration for ShopForge.
 *
 * Vite is FAST because:
 * 1. Dev mode: serves ES modules directly (no bundling needed)
 * 2. Build mode: uses Rollup (tree-shaking, code splitting)
 * 3. HMR: instant updates without full page reload
 */
import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import vuetify from "vite-plugin-vuetify";
export default defineConfig({
    plugins: [
        vue(),
        vuetify({ autoImport: true }), // Auto-import Vuetify components
    ],
    resolve: {
        alias: {
            // @ maps to src/ — so `import Foo from '@/components/Foo.vue'` works
            "@": fileURLToPath(new URL("./shopforge/webapp/src", import.meta.url)),
        },
    },
    // Dev server configuration
    server: {
        port: 5174,
        host: "0.0.0.0", // Allow access from Docker host
        strictPort: true,
        watch: {
            usePolling: true, // Required for Docker volumes (filesystem events don't propagate)
        },
    },
    // Build configuration
    build: {
        outDir: "shopforge/webapp/dist",
        manifest: true, // Generate manifest.json for django-vite
        rollupOptions: {
            input: {
                // Multiple entry points for different page types
                main: "shopforge/webapp/src/main.ts",
                login: "shopforge/webapp/src/login.ts",
            },
            output: {
                // Split large dependencies into separate chunks
                manualChunks: {
                    vue: ["vue", "vue-router", "pinia"],
                    vuetify: ["vuetify"],
                },
            },
        },
    },
    // CSS configuration
    css: {
        preprocessorOptions: {
            scss: {
                // Make SCSS variables available in all components without importing
                additionalData: `@use "@/assets/styles/variables" as *;\n`,
            },
        },
    },
});
