/**
 * Login page entry point.
 *
 * Separate bundle from main.ts so the login page loads independently
 * without pulling in the full app (router, pinia, etc.).
 */
import "./assets/styles/main.css";

import { createPinia } from "pinia";
import { createApp } from "vue";

import { vuetify } from "./plugins/vuetify";
import LoginView from "./views/LoginView.vue";

const app = createApp(LoginView);

app.use(createPinia());
app.use(vuetify);

app.mount("#login-app");
