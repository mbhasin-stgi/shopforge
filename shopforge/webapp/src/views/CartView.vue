<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import { useCartStore } from "@/stores/cart";

const cart = useCartStore();
const router = useRouter();

const isEmpty = computed(() => cart.items.length === 0);

function checkout() {
  router.push({ name: "checkout" });
}
</script>

<template>
  <v-container class="py-8" style="max-width: 900px">
    <!-- Header -->
    <div class="mb-6">
      <h1
        class="text-h4 font-weight-bold mb-1"
        style="color: #1e293b; letter-spacing: -0.5px"
      >
        Shopping Cart
      </h1>
      <p class="text-body-1" style="color: #64748b">
        {{
          isEmpty
            ? "Your cart is empty"
            : `${cart.itemCount} item${cart.itemCount !== 1 ? "s" : ""} in your cart`
        }}
      </p>
    </div>

    <!-- Empty state -->
    <v-card
      v-if="isEmpty"
      rounded="xl"
      elevation="0"
      border
      class="pa-12 text-center"
    >
      <v-icon size="64" color="grey-300" class="mb-4"
        >fa:fas fa-cart-shopping</v-icon
      >
      <h3 class="text-h6 font-weight-medium mb-2" style="color: #475569">
        Nothing here yet
      </h3>
      <p class="text-body-2 mb-6" style="color: #94a3b8">
        Browse our catalog and add items to your cart.
      </p>
      <v-btn
        color="primary"
        variant="flat"
        rounded="xl"
        :to="{ name: 'products' }"
      >
        Browse Products
      </v-btn>
    </v-card>

    <!-- Cart items -->
    <template v-else>
      <div class="d-flex flex-column gap-3 mb-6">
        <v-card
          v-for="item in cart.items"
          :key="item.productId"
          rounded="xl"
          elevation="0"
          border
        >
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-4">
              <!-- Thumbnail -->
              <v-img
                :src="item.primaryImage ?? ''"
                :alt="item.productName"
                width="72"
                height="72"
                rounded="lg"
                cover
                style="flex-shrink: 0; background: #f1f5f9"
              >
                <template #error>
                  <div
                    class="d-flex align-center justify-center fill-height"
                    style="background: #f1f5f9"
                  >
                    <v-icon size="24" color="grey-300">fa:far fa-image</v-icon>
                  </div>
                </template>
              </v-img>

              <!-- Info -->
              <div style="flex: 1; min-width: 0">
                <RouterLink
                  :to="{
                    name: 'product-detail',
                    params: { slug: item.productSlug },
                  }"
                  class="text-body-1 font-weight-medium text-decoration-none"
                  style="color: #1e293b"
                >
                  {{ item.productName }}
                </RouterLink>
                <p class="text-body-2 mt-1" style="color: #64748b">
                  ${{ item.price }} × {{ item.quantity }}
                </p>
              </div>

              <!-- Qty controls -->
              <div
                class="d-flex align-center border rounded-lg overflow-hidden"
                style="flex-shrink: 0"
              >
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  :disabled="item.quantity <= 1"
                  @click="
                    cart.updateQuantity(item.productId, item.quantity - 1)
                  "
                >
                  <v-icon size="14">fa:fas fa-minus</v-icon>
                </v-btn>
                <span class="px-3 text-body-2 font-weight-medium">{{
                  item.quantity
                }}</span>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="
                    cart.updateQuantity(item.productId, item.quantity + 1)
                  "
                >
                  <v-icon size="14">fa:fas fa-plus</v-icon>
                </v-btn>
              </div>

              <!-- Line total -->
              <div class="text-right" style="min-width: 72px; flex-shrink: 0">
                <p class="text-body-1 font-weight-bold" style="color: #1565c0">
                  ${{ (parseFloat(item.price) * item.quantity).toFixed(2) }}
                </p>
              </div>

              <!-- Remove -->
              <v-btn
                icon
                variant="text"
                size="small"
                color="error"
                @click="cart.removeItem(item.productId)"
              >
                <v-icon size="16">fa:fas fa-trash</v-icon>
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </div>

      <!-- Summary -->
      <v-card rounded="xl" elevation="0" border>
        <v-card-text class="pa-6">
          <div class="d-flex justify-space-between mb-3">
            <span class="text-body-1" style="color: #64748b">Subtotal</span>
            <span class="text-body-1 font-weight-medium"
              >${{ cart.total }}</span
            >
          </div>
          <v-divider class="mb-4" />
          <div class="d-flex justify-space-between mb-5">
            <span class="text-h6 font-weight-bold" style="color: #1e293b"
              >Total</span
            >
            <span class="text-h6 font-weight-bold" style="color: #1565c0"
              >${{ cart.total }}</span
            >
          </div>
          <v-btn
            color="primary"
            variant="flat"
            rounded="xl"
            block
            size="large"
            style="height: 52px; font-weight: 600"
            @click="checkout"
          >
            Proceed to Checkout
          </v-btn>
          <v-btn variant="text" block class="mt-2" :to="{ name: 'products' }">
            Continue Shopping
          </v-btn>
        </v-card-text>
      </v-card>
    </template>
  </v-container>
</template>
