/**
 * Vue Router configuration.
 *
 * Defines all client-side routes and navigation guards.
 * Main routes use eager imports to avoid first-click delay.
 * Heavy/secondary routes use lazy imports for code splitting.
 */
import { createRouter, createWebHistory } from "vue-router";

// Eager imports — zero delay on first navigation for core pages
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import ProductListView from "@/views/ProductListView.vue";
import CartView from "@/views/CartView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
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
      path: "/orders",
      name: "orders",
      component: () => import("@/views/OrderListView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
  ],
});

// Navigation guard: redirect to login if route requires auth
router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!localStorage.getItem("auth_token");
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "login", query: { redirect: to.fullPath } });
  } else {
    next();
  }
});
