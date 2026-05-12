import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "../auth";

const MOCK_USER = {
  id: "1",
  email: "test@test.com",
  first_name: "Test",
  last_name: "User",
  role: "CUSTOMER",
  phone_number: "",
};

// Mock the API module
vi.mock("@/services/api", () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

describe("Auth Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("starts unauthenticated", () => {
    const store = useAuthStore();
    expect(store.isAuthenticated).toBe(false);
    expect(store.user).toBeNull();
  });

  it("isAuthenticated is true when token is set", () => {
    localStorage.setItem("auth_token", "fake-token");
    setActivePinia(createPinia());
    const store = useAuthStore();
    expect(store.isAuthenticated).toBe(true);
  });

  it("logout clears token and user", async () => {
    const { api } = await import("@/services/api");
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({});
    const store = useAuthStore();
    store.token = "test-token";
    store.user = MOCK_USER;

    await store.logout();

    expect(store.token).toBeNull();
    expect(store.user).toBeNull();
    expect(localStorage.getItem("auth_token")).toBeNull();
  });

  it("logout clears state even if server call fails", async () => {
    const { api } = await import("@/services/api");
    (api.post as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error("Network error"),
    );
    const store = useAuthStore();
    store.token = "dead-token";
    store.user = MOCK_USER;

    await store.logout();

    expect(store.token).toBeNull();
    expect(store.user).toBeNull();
  });

  it("login sets token and user from response", async () => {
    const { api } = await import("@/services/api");
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: { key: "my-token" },
    });
    (api.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: MOCK_USER,
    });
    const store = useAuthStore();

    await store.login("test@test.com", "password");

    expect(store.token).toBe("my-token");
    expect(store.user?.email).toBe("test@test.com");
    expect(localStorage.getItem("auth_token")).toBe("my-token");
  });

  it("fullName returns first + last name", () => {
    const store = useAuthStore();
    store.user = MOCK_USER;
    expect(store.fullName).toBe("Test User");
  });

  it("fullName falls back to email when name is empty", () => {
    const store = useAuthStore();
    store.user = { ...MOCK_USER, first_name: "", last_name: "" };
    expect(store.fullName).toBe("test@test.com");
  });

  it("isAdmin is false for regular user", () => {
    const store = useAuthStore();
    store.user = MOCK_USER;
    expect(store.isAdmin).toBe(false);
  });

  it("isAdmin is true for ADMIN role", () => {
    const store = useAuthStore();
    store.user = { ...MOCK_USER, role: "ADMIN" };
    expect(store.isAdmin).toBe(true);
  });
});
