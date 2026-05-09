/**
 * Main application entry point.
 *
 * This file bootstraps the Vue app with all plugins:
 * router, state management, component library, etc.
 */
// Global styles
import "./assets/styles/main.css";

import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import { vuetify } from "./plugins/vuetify";
import { router } from "./router";

const app = createApp(App);

// Install plugins
app.use(createPinia()); // State management
app.use(router); // Client-side routing
app.use(vuetify); // UI component library

// Mount the app to the DOM
app.mount("#app");
