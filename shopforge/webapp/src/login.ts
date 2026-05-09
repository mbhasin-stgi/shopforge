/**
 * Login page entry point.
 *
 * Separate bundle from main.ts so the login page loads independently
 * without pulling in the full app (router, pinia, etc.).
 */
import { createApp } from "vue";
import { createPinia } from "pinia";

import LoginView from "./views/LoginView.vue";
import { vuetify } from "./plugins/vuetify";

import "./assets/styles/main.css";

const app = createApp(LoginView);

app.use(createPinia());
app.use(vuetify);

app.mount("#login-app");
