/**
 * Axios instance with interceptors for auth and CSRF handling.
 *
 * 1. Reads the Django csrftoken cookie and adds X-CSRFToken header automatically
 * 2. Adds the auth token (Token-based) to every request
 * 3. Handles 401 — redirects to login
 */
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  withCredentials: true, // Send cookies (including csrftoken) with every request
  xsrfCookieName: "csrftoken", // Django sets this cookie on first response
  xsrfHeaderName: "X-CSRFToken", // Django's CSRF middleware reads this header
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach Token auth header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Response interceptor: handle 401 (token expired / invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);
