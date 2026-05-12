/**
 * Vue Router configuration.
 *
 * Navigation guard uses the Pinia auth store (not localStorage directly)
 * so the authentication check is reactive and consistent.
 *
 * Core pages use eager imports (zero first-click delay).
 * Secondary pages use lazy imports for code splitting.
 */
import { createRouter, createWebHistory } from "vue-router";

// Eager imports — zero delay for the most visited pages
import CartView from "@/views/CartView.vue";
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import ProductListView from "@/views/ProductListView.vue";

export const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: (_to, _from, savedPosition) => savedPosition ?? { top: 0 },
  routes: [
    // ─── Public routes ──────────────────────────────────────────
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/products",
      name: "products",
      component: ProductListView,
    },
    {
      path: "/products/:slug",
      name: "product-detail",
      component: () => import("@/views/ProductDetailView.vue"),
      props: true,
    },
    {
      path: "/cart",
      name: "cart",
      component: CartView,
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
    },

    // ─── Auth-required routes ────────────────────────────────────
    {
      path: "/checkout",
      name: "checkout",
      component: () => import("@/views/CheckoutView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/orders",
      name: "orders",
      component: () => import("@/views/OrderListView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/orders/:id",
      name: "order-detail",
      component: () => import("@/views/OrderDetailView.vue"),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: "/profile",
      name: "profile",
      component: () => import("@/views/UserProfileView.vue"),
      meta: { requiresAuth: true },
    },

    // ─── 404 catch-all (must be last) ────────────────────────────
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
});

// Navigation guard — uses Pinia store so the check is reactive.
// We lazy-import to avoid the Pinia-before-app circular init issue.
router.beforeEach(async (to, _from, next) => {
  if (!to.meta.requiresAuth) {
    next();
    return;
  }

  // Import here (after app is created) to avoid circular dependency
  const { useAuthStore } = await import("@/stores/auth");
  const auth = useAuthStore();

  // Bootstrap: restore user profile from a persisted token on page refresh
  if (!auth.user && auth.isAuthenticated) {
    await auth.bootstrap();
  }

  if (!auth.isAuthenticated) {
    next({ name: "login", query: { redirect: to.fullPath } });
  } else {
    next();
  }
});
