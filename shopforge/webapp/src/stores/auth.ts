/**
 * Auth store — manages authentication state.
 *
 * dj-rest-auth returns { key: "token" } on login.
 * The Django User model uses snake_case field names.
 */
import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { api } from "@/services/api";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone_number: string;
}

export const useAuthStore = defineStore("auth", () => {
  // ─── State ─────────────────────────────────────────────────────
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem("auth_token"));

  // ─── Getters ───────────────────────────────────────────────────
  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === "ADMIN");
  const fullName = computed(() =>
    user.value
      ? `${user.value.first_name} ${user.value.last_name}`.trim() ||
        user.value.email
      : "",
  );

  // ─── Actions ───────────────────────────────────────────────────
  async function login(email: string, password: string) {
    // dj-rest-auth returns { key: "<token>" } — NOT { token: "..." }
    const response = await api.post("/auth/login/", { email, password });
    token.value = response.data.key;
    localStorage.setItem("auth_token", response.data.key);
    await fetchProfile();
  }

  async function logout() {
    try {
      // Invalidate the token on the server before clearing local state
      await api.post("/auth/logout/");
    } catch {
      // Always clear local state even if the server call fails
    } finally {
      token.value = null;
      user.value = null;
      localStorage.removeItem("auth_token");
    }
  }

  async function register(
    email: string,
    password1: string,
    password2: string,
    firstName: string,
    lastName: string,
  ) {
    const response = await api.post("/auth/registration/", {
      email,
      password1,
      password2,
      first_name: firstName,
      last_name: lastName,
    });
    // dj-rest-auth registration returns { key: "..." } on auto-login
    if (response.data.key) {
      token.value = response.data.key;
      localStorage.setItem("auth_token", response.data.key);
      await fetchProfile();
    }
  }

  async function updateProfile(data: Partial<User>) {
    const response = await api.patch("/users/me/", data);
    user.value = response.data;
  }

  async function fetchProfile() {
    if (!token.value) return;
    const response = await api.get("/users/me/");
    user.value = response.data;
  }

  /**
   * Bootstrap: if a token exists in localStorage but we don't have user info
   * yet (e.g. after a page refresh), fetch the profile silently.
   */
  async function bootstrap() {
    if (token.value && !user.value) {
      await fetchProfile().catch(() => {
        // Token is stale — clear it
        token.value = null;
        localStorage.removeItem("auth_token");
      });
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    fullName,
    login,
    logout,
    register,
    updateProfile,
    fetchProfile,
    bootstrap,
  };
});
