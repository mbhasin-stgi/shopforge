<script setup lang="ts">
import { onMounted, ref } from "vue";

import OrderStatusBadge from "@/components/OrderStatusBadge.vue";
import { api } from "@/services/api";

interface Order {
  id: string;
  order_number: string;
  status: string;
  payment_status: string;
  total: string;
  subtotal: string;
  item_count?: number;
  created_at: string;
}

const orders = ref<Order[]>([]);
const loading = ref(true);
const error = ref(false);

async function fetchOrders() {
  loading.value = true;
  error.value = false;
  try {
    const response = await api.get("/orders/");
    orders.value = response.data.results ?? response.data;
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

onMounted(fetchOrders);
</script>

<template>
  <v-container class="py-8" style="max-width: 900px">
    <!-- Page header -->
    <div class="mb-6">
      <h1
        class="text-h4 font-weight-bold mb-1"
        style="color: #1e293b; letter-spacing: -0.5px"
      >
        My Orders
      </h1>
      <p class="text-body-1" style="color: #64748b">
        Track and manage your purchase history
      </p>
    </div>

    <!-- Error -->
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      rounded="xl"
      class="mb-4"
    >
      Failed to load orders.
      <template #append>
        <v-btn variant="text" @click="fetchOrders">Retry</v-btn>
      </template>
    </v-alert>

    <!-- Orders list -->
    <div v-if="!loading && orders.length" class="d-flex flex-column gap-3">
      <v-card
        v-for="order in orders"
        :key="order.id"
        rounded="xl"
        elevation="0"
        border
        class="pa-0"
      >
        <v-card-text class="pa-5">
          <div class="d-flex align-start justify-space-between flex-wrap gap-3">
            <!-- Left: order info -->
            <div>
              <div class="d-flex align-center gap-2 mb-1">
                <span
                  class="text-body-1 font-weight-bold"
                  style="color: #1e293b"
                >
                  {{ order.order_number }}
                </span>
                <OrderStatusBadge :status="order.status" />
              </div>
              <p class="text-body-2" style="color: #64748b">
                Placed on {{ formatDate(order.created_at) }}
              </p>
            </div>

            <!-- Right: total -->
            <div class="text-right">
              <p class="text-h6 font-weight-bold" style="color: #1565c0">
                ${{ order.total }}
              </p>
              <p class="text-caption" style="color: #94a3b8">
                Payment:
                <span
                  :class="
                    order.payment_status === 'PAID'
                      ? 'text-success'
                      : 'text-warning'
                  "
                >
                  {{ order.payment_status }}
                </span>
              </p>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Empty state -->
    <v-card
      v-else-if="!loading && !orders.length && !error"
      rounded="xl"
      elevation="0"
      border
      class="pa-12 text-center"
    >
      <v-icon size="64" color="grey-300" class="mb-4"
        >fa:fas fa-box-open</v-icon
      >
      <h3 class="text-h6 font-weight-medium mb-2" style="color: #475569">
        No orders yet
      </h3>
      <p class="text-body-2 mb-6" style="color: #94a3b8">
        Your orders will appear here once you make a purchase.
      </p>
      <v-btn
        color="primary"
        variant="flat"
        rounded="xl"
        :to="{ name: 'products' }"
      >
        Start Shopping
      </v-btn>
    </v-card>

    <!-- Loading -->
    <div v-else-if="loading" class="d-flex flex-column gap-3">
      <v-card v-for="n in 3" :key="n" rounded="xl" elevation="0" border>
        <v-card-text class="pa-5">
          <v-skeleton-loader type="text" class="mb-2" width="50%" />
          <v-skeleton-loader type="text" width="30%" />
        </v-card-text>
      </v-card>
    </div>
  </v-container>
</template>
