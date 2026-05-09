<script setup lang="ts">
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { useCartStore } from "@/stores/cart";
import { useNotification } from "@/composables/useNotification";

const router = useRouter();
const auth = useAuthStore();
const cart = useCartStore();
const { notify } = useNotification();

async function handleLogout() {
  await auth.logout();
  notify("You have been signed out.", "info");
  router.push({ name: "home" });
}
</script>

<template>
  <v-app-bar elevation="0" border="b" color="white" height="64">
    <!-- Brand -->
    <v-app-bar-title class="pl-2">
      <RouterLink
        :to="{ name: 'home' }"
        class="text-decoration-none d-flex align-center gap-2"
        style="color: inherit"
      >
        <v-icon color="primary" size="28">fa:fas fa-store</v-icon>
        <span class="text-h6 font-weight-bold" style="color: #1565C0; letter-spacing: -0.3px">
          ShopForge
        </span>
      </RouterLink>
    </v-app-bar-title>

    <template #append>
      <!-- Nav links -->
      <v-btn
        :to="{ name: 'products' }"
        variant="text"
        size="small"
        class="text-body-2 font-weight-medium mr-1"
        rounded="lg"
      >
        Products
      </v-btn>

      <v-divider vertical class="mx-2 my-3" />

      <!-- Cart icon -->
      <v-btn icon variant="text" rounded="lg" class="mr-1" :to="{ name: 'cart' }">
        <v-badge
          :content="cart.itemCount"
          :model-value="cart.itemCount > 0"
          color="error"
          floating
        >
          <v-icon>fa:fas fa-cart-shopping</v-icon>
        </v-badge>
      </v-btn>

      <!-- Authenticated user menu -->
      <template v-if="auth.isAuthenticated">
        <v-menu transition="slide-y-transition">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              variant="tonal"
              color="primary"
              rounded="lg"
              size="small"
              class="ml-1 mr-2"
              prepend-icon="fa:fas fa-user-circle"
            >
              {{ auth.fullName || auth.user?.email }}
              <v-icon end>fa:fas fa-chevron-down</v-icon>
            </v-btn>
          </template>

          <v-list width="200" rounded="lg" elevation="4" class="mt-1">
            <v-list-item
              :to="{ name: 'orders' }"
              prepend-icon="fa:fas fa-box"
              title="My Orders"
              rounded="lg"
            />
            <v-divider class="my-1" />
            <v-list-item
              prepend-icon="fa:fas fa-right-from-bracket"
              title="Sign Out"
              base-color="error"
              rounded="lg"
              @click="handleLogout"
            />
          </v-list>
        </v-menu>
      </template>

      <!-- Guest sign-in button -->
      <v-btn
        v-else
        :to="{ name: 'login' }"
        color="primary"
        variant="flat"
        rounded="lg"
        size="small"
        class="mr-2 ml-1"
        prepend-icon="fa:fas fa-right-to-bracket"
      >
        Sign In
      </v-btn>
    </template>
  </v-app-bar>
</template>

