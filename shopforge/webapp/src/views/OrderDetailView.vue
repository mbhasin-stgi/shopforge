<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useOrders } from "@/composables/useOrders";

const route = useRoute();
const router = useRouter();
const { currentOrder, loading, error, fetchOrder, cancelOrder } = useOrders();

const cancelLoading = ref(false);
const cancelError = ref<string | null>(null);
const showCancelDialog = ref(false);

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  PENDING: { label: "Pending", color: "warning" },
  CONFIRMED: { label: "Confirmed", color: "info" },
  PROCESSING: { label: "Processing", color: "info" },
  SHIPPED: { label: "Shipped", color: "primary" },
  DELIVERED: { label: "Delivered", color: "success" },
  CANCELLED: { label: "Cancelled", color: "error" },
  REFUNDED: { label: "Refunded", color: "secondary" },
};

const PAYMENT_LABELS: Record<string, { label: string; color: string }> = {
  PENDING: { label: "Payment Pending", color: "warning" },
  PAID: { label: "Paid", color: "success" },
  FAILED: { label: "Payment Failed", color: "error" },
  REFUNDED: { label: "Refunded", color: "secondary" },
};

const statusInfo = computed(() => {
  const s = currentOrder.value?.status ?? "";
  return STATUS_LABELS[s] ?? { label: s, color: "default" };
});

const paymentInfo = computed(() => {
  const s = currentOrder.value?.payment_status ?? "";
  return PAYMENT_LABELS[s] ?? { label: s, color: "default" };
});

const canCancel = computed(() =>
  ["PENDING", "CONFIRMED"].includes(currentOrder.value?.status ?? ""),
);

const formattedDate = (iso: string) =>
  new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

async function handleCancel() {
  cancelLoading.value = true;
  cancelError.value = null;
  const result = await cancelOrder(route.params.id as string);
  cancelLoading.value = false;
  showCancelDialog.value = false;
  if (!result) {
    cancelError.value = "Failed to cancel order.";
  }
}

onMounted(async () => {
  const id = route.params.id as string;
  if (!id) {
    router.push({ name: "orders" });
    return;
  }
  await fetchOrder(id);
});
</script>

<template>
  <v-container class="py-8" style="max-width: 800px">
    <!-- Back nav -->
    <div class="mb-5">
      <v-btn
        variant="text"
        :to="{ name: 'orders' }"
        prepend-icon="fa:fas fa-arrow-left"
      >
        All Orders
      </v-btn>
    </div>

    <!-- Loading -->
    <template v-if="loading">
      <v-card rounded="xl" border elevation="0" class="pa-8">
        <v-skeleton-loader type="article" />
      </v-card>
    </template>

    <!-- Error -->
    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      rounded="xl"
      class="mb-6"
    >
      {{ error }}
    </v-alert>

    <!-- Order content -->
    <template v-else-if="currentOrder">
      <!-- Header card -->
      <v-card rounded="xl" border elevation="0" class="pa-6 mb-4">
        <div class="d-flex align-start justify-space-between flex-wrap gap-3">
          <div>
            <h1
              class="text-h5 font-weight-bold mb-1"
              style="color: #1e293b; letter-spacing: -0.5px"
            >
              Order {{ currentOrder.order_number }}
            </h1>
            <p class="text-body-2" style="color: #64748b">
              Placed on {{ formattedDate(currentOrder.created_at) }}
            </p>
          </div>
          <div class="d-flex gap-2 flex-wrap">
            <v-chip :color="statusInfo.color" label>{{
              statusInfo.label
            }}</v-chip>
            <v-chip :color="paymentInfo.color" label variant="tonal">
              {{ paymentInfo.label }}
            </v-chip>
          </div>
        </div>

        <!-- Tracking number -->
        <div
          v-if="currentOrder.tracking_number"
          class="mt-4 pa-3 border rounded-lg d-flex align-center gap-2"
          style="background: #f0f9ff"
        >
          <v-icon size="16" color="primary">fa:fas fa-truck</v-icon>
          <span class="text-body-2">
            Tracking: <strong>{{ currentOrder.tracking_number }}</strong>
          </span>
        </div>
      </v-card>

      <!-- Line items -->
      <v-card rounded="xl" border elevation="0" class="pa-6 mb-4">
        <h2
          class="text-subtitle-1 font-weight-bold mb-4"
          style="color: #1e293b"
        >
          Items
        </h2>
        <div
          v-for="item in currentOrder.items"
          :key="item.id"
          class="d-flex justify-space-between align-center mb-3"
        >
          <div>
            <span class="text-body-2 font-weight-medium">{{
              item.product_name
            }}</span>
            <span class="text-caption ml-2" style="color: #94a3b8">
              SKU: {{ item.product_sku }}
            </span>
          </div>
          <div class="text-right">
            <span class="text-body-2" style="color: #64748b"
              >×{{ item.quantity }}</span
            >
            <span class="text-body-2 font-weight-medium ml-3">
              ${{
                (parseFloat(item.price_at_purchase) * item.quantity).toFixed(2)
              }}
            </span>
          </div>
        </div>

        <v-divider class="my-4" />

        <!-- Totals -->
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2" style="color: #64748b">Subtotal</span>
          <span class="text-body-2">${{ currentOrder.subtotal }}</span>
        </div>
        <div
          v-if="parseFloat(currentOrder.discount_amount) > 0"
          class="d-flex justify-space-between mb-2"
        >
          <span class="text-body-2" style="color: #16a34a">Discount</span>
          <span class="text-body-2" style="color: #16a34a">
            −${{ currentOrder.discount_amount }}
          </span>
        </div>
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2" style="color: #64748b">Tax</span>
          <span class="text-body-2">${{ currentOrder.tax_amount }}</span>
        </div>
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2" style="color: #64748b">Shipping</span>
          <span class="text-body-2">${{ currentOrder.shipping_cost }}</span>
        </div>
        <v-divider class="my-3" />
        <div class="d-flex justify-space-between">
          <span class="text-body-1 font-weight-bold" style="color: #1e293b"
            >Total</span
          >
          <span class="text-body-1 font-weight-bold" style="color: #1565c0">
            ${{ currentOrder.total }}
          </span>
        </div>
      </v-card>

      <!-- Shipping address -->
      <v-card rounded="xl" border elevation="0" class="pa-6 mb-4">
        <h2
          class="text-subtitle-1 font-weight-bold mb-3"
          style="color: #1e293b"
        >
          Shipping Address
        </h2>
        <p class="text-body-2" style="color: #475569; line-height: 1.8">
          {{ currentOrder.shipping_address_line1 }}<br />
          <span v-if="currentOrder.shipping_address_line2">
            {{ currentOrder.shipping_address_line2 }}<br />
          </span>
          {{ currentOrder.shipping_city }}, {{ currentOrder.shipping_state }}
          {{ currentOrder.shipping_postal_code }}<br />
          {{ currentOrder.shipping_country }}
        </p>
      </v-card>

      <!-- Cancel error -->
      <v-alert
        v-if="cancelError"
        type="error"
        variant="tonal"
        rounded="xl"
        class="mb-4"
        closable
        @click:close="cancelError = null"
      >
        {{ cancelError }}
      </v-alert>

      <!-- Actions -->
      <div class="d-flex justify-end">
        <v-btn
          v-if="canCancel"
          color="error"
          variant="outlined"
          rounded="xl"
          @click="showCancelDialog = true"
        >
          Cancel Order
        </v-btn>
      </div>
    </template>

    <!-- Cancel confirmation dialog -->
    <v-dialog v-model="showCancelDialog" max-width="400">
      <v-card rounded="xl">
        <v-card-text class="pa-6">
          <h3 class="text-h6 font-weight-bold mb-2" style="color: #1e293b">
            Cancel Order?
          </h3>
          <p class="text-body-2" style="color: #475569">
            This action cannot be undone. Any reserved inventory will be
            released.
          </p>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0 gap-2">
          <v-spacer />
          <v-btn variant="text" @click="showCancelDialog = false"
            >Keep Order</v-btn
          >
          <v-btn
            color="error"
            variant="flat"
            rounded="xl"
            :loading="cancelLoading"
            @click="handleCancel"
          >
            Yes, Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
