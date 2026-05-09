import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "../auth";

// Mock the API module
vi.mock("@/services/api", () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
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

  it("logout clears state", async () => {
    const store = useAuthStore();
    store.token = "test-token";
    store.user = {
      id: "1",
      email: "test@test.com",
      firstName: "Test",
      lastName: "User",
      role: "CUSTOMER",
    };

    await store.logout();

    expect(store.token).toBeNull();
    expect(store.user).toBeNull();
    expect(localStorage.getItem("auth_token")).toBeNull();
  });
});
