<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import { api } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import { useCartStore } from "@/stores/cart";

const router = useRouter();
const cart = useCartStore();
const auth = useAuthStore();

// ─── Step management ─────────────────────────────────────────────
const step = ref<1 | 2 | 3>(1);

// ─── Step 1: Shipping address ────────────────────────────────────
const shipping = ref({
  fullName: auth.user?.first_name + " " + auth.user?.last_name ?? "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  postalCode: "",
  country: "US",
});

// ─── Step 2: Order review ─────────────────────────────────────────
const couponCode = ref("");
const couponError = ref<string | null>(null);
const couponDiscount = ref<number | null>(null);
const couponLoading = ref(false);

const subtotal = computed(() => cart.total);
const discount = computed(() => couponDiscount.value ?? 0);
const total = computed(() =>
  Math.max(0, Number(subtotal.value) - discount.value).toFixed(2),
);

async function validateCoupon() {
  if (!couponCode.value.trim()) return;
  couponLoading.value = true;
  couponError.value = null;
  couponDiscount.value = null;
  try {
    const response = await api.post("/coupons/validate/", {
      code: couponCode.value,
      subtotal: subtotal.value,
    });
    couponDiscount.value = parseFloat(response.data.discount_amount);
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { error?: string } } };
    couponError.value =
      axiosErr?.response?.data?.error ?? "Invalid coupon code.";
  } finally {
    couponLoading.value = false;
  }
}

// ─── Step 3: Submit order ─────────────────────────────────────────
const submitting = ref(false);
const submitError = ref<string | null>(null);
const placedOrder = ref<{ id: string; order_number: string } | null>(null);

async function placeOrder() {
  submitting.value = true;
  submitError.value = null;
  try {
    const payload: Record<string, unknown> = {
      shipping_address_line1: shipping.value.line1,
      shipping_address_line2: shipping.value.line2,
      shipping_city: shipping.value.city,
      shipping_state: shipping.value.state,
      shipping_postal_code: shipping.value.postalCode,
      shipping_country: shipping.value.country,
      items: cart.items.map((i) => ({
        product_id: i.productId,
        quantity: i.quantity,
      })),
    };
    if (couponCode.value.trim()) {
      payload.coupon_code = couponCode.value;
    }
    const response = await api.post("/orders/", payload);
    placedOrder.value = {
      id: response.data.id,
      order_number: response.data.order_number,
    };
    cart.clearCart();
    step.value = 3;
  } catch (err: unknown) {
    const axiosErr = err as {
      response?: { data?: { error?: string; non_field_errors?: string[] } };
    };
    submitError.value =
      axiosErr?.response?.data?.error ??
      axiosErr?.response?.data?.non_field_errors?.[0] ??
      "Could not place order. Please try again.";
  } finally {
    submitting.value = false;
  }
}

// ─── Helpers ─────────────────────────────────────────────────────
const shippingIsValid = computed(
  () =>
    shipping.value.line1.trim() &&
    shipping.value.city.trim() &&
    shipping.value.state.trim() &&
    shipping.value.postalCode.trim(),
);
</script>

<template>
  <v-container class="py-8" style="max-width: 800px">
    <!-- Header with step indicator -->
    <div class="mb-8">
      <h1
        class="text-h4 font-weight-bold mb-4"
        style="color: #1e293b; letter-spacing: -0.5px"
      >
        Checkout
      </h1>
      <v-stepper
        :model-value="step"
        alt-labels
        flat
        class="border rounded-xl overflow-hidden"
      >
        <v-stepper-header>
          <v-stepper-item value="1" title="Shipping" :complete="step > 1" />
          <v-divider />
          <v-stepper-item value="2" title="Review" :complete="step > 2" />
          <v-divider />
          <v-stepper-item
            value="3"
            title="Confirmation"
            :complete="step === 3"
          />
        </v-stepper-header>
      </v-stepper>
    </div>

    <!-- ────────────────────────────────── STEP 1: Shipping ──── -->
    <template v-if="step === 1">
      <v-card rounded="xl" border elevation="0" class="pa-6 mb-6">
        <h2 class="text-h6 font-weight-bold mb-5" style="color: #1e293b">
          Shipping Address
        </h2>
        <v-text-field
          v-model="shipping.fullName"
          label="Full name"
          variant="outlined"
          density="comfortable"
          rounded="lg"
          class="mb-3"
        />
        <v-text-field
          v-model="shipping.line1"
          label="Address line 1"
          variant="outlined"
          density="comfortable"
          rounded="lg"
          class="mb-3"
        />
        <v-text-field
          v-model="shipping.line2"
          label="Address line 2 (optional)"
          variant="outlined"
          density="comfortable"
          rounded="lg"
          class="mb-3"
        />
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="shipping.city"
              label="City"
              variant="outlined"
              density="comfortable"
              rounded="lg"
            />
          </v-col>
          <v-col cols="6" sm="3">
            <v-text-field
              v-model="shipping.state"
              label="State"
              variant="outlined"
              density="comfortable"
              rounded="lg"
            />
          </v-col>
          <v-col cols="6" sm="3">
            <v-text-field
              v-model="shipping.postalCode"
              label="ZIP / Postal code"
              variant="outlined"
              density="comfortable"
              rounded="lg"
            />
          </v-col>
        </v-row>
        <v-select
          v-model="shipping.country"
          :items="['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'IN', 'JP', 'SG']"
          label="Country"
          variant="outlined"
          density="comfortable"
          rounded="lg"
          class="mt-2"
        />
      </v-card>

      <div class="d-flex justify-end gap-3">
        <v-btn variant="text" :to="{ name: 'cart' }">Back to Cart</v-btn>
        <v-btn
          color="primary"
          variant="flat"
          rounded="xl"
          :disabled="!shippingIsValid"
          @click="step = 2"
        >
          Continue to Review
          <v-icon end>fa:fas fa-arrow-right</v-icon>
        </v-btn>
      </div>
    </template>

    <!-- ────────────────────────────────── STEP 2: Review ──── -->
    <template v-if="step === 2">
      <!-- Items -->
      <v-card rounded="xl" border elevation="0" class="pa-6 mb-4">
        <h2 class="text-h6 font-weight-bold mb-4" style="color: #1e293b">
          Order Summary
        </h2>
        <div
          v-for="item in cart.items"
          :key="item.productId"
          class="d-flex justify-space-between align-center mb-3"
        >
          <div>
            <span class="text-body-2 font-weight-medium">{{
              item.productName
            }}</span>
            <span class="text-body-2 ml-2" style="color: #94a3b8"
              >×{{ item.quantity }}</span
            >
          </div>
          <span class="text-body-2 font-weight-medium">
            ${{ (parseFloat(item.price) * item.quantity).toFixed(2) }}
          </span>
        </div>
        <v-divider class="my-4" />

        <!-- Coupon -->
        <div class="d-flex gap-2 mb-4">
          <v-text-field
            v-model="couponCode"
            label="Coupon code"
            variant="outlined"
            density="compact"
            rounded="lg"
            hide-details
            style="max-width: 220px"
            @keyup.enter="validateCoupon"
          />
          <v-btn
            variant="tonal"
            color="primary"
            :loading="couponLoading"
            @click="validateCoupon"
          >
            Apply
          </v-btn>
        </div>
        <v-alert
          v-if="couponError"
          type="error"
          variant="tonal"
          density="compact"
          rounded="lg"
          class="mb-3"
        >
          {{ couponError }}
        </v-alert>
        <v-alert
          v-if="couponDiscount !== null"
          type="success"
          variant="tonal"
          density="compact"
          rounded="lg"
          class="mb-3"
        >
          Coupon applied: −${{ couponDiscount.toFixed(2) }}
        </v-alert>

        <!-- Totals -->
        <div class="d-flex justify-space-between mb-2">
          <span style="color: #64748b">Subtotal</span>
          <span>${{ subtotal }}</span>
        </div>
        <div v-if="discount > 0" class="d-flex justify-space-between mb-2">
          <span style="color: #16a34a">Discount</span>
          <span style="color: #16a34a">−${{ discount.toFixed(2) }}</span>
        </div>
        <v-divider class="my-3" />
        <div class="d-flex justify-space-between">
          <span class="text-body-1 font-weight-bold" style="color: #1e293b"
            >Total</span
          >
          <span class="text-body-1 font-weight-bold" style="color: #1565c0"
            >${{ total }}</span
          >
        </div>
      </v-card>

      <!-- Shipping summary -->
      <v-card rounded="xl" border elevation="0" class="pa-5 mb-6">
        <div class="d-flex justify-space-between align-center mb-2">
          <h3 class="text-body-1 font-weight-bold" style="color: #1e293b">
            Ship To
          </h3>
          <v-btn variant="text" size="small" @click="step = 1">Edit</v-btn>
        </div>
        <p class="text-body-2" style="color: #475569">
          {{ shipping.fullName }}<br />
          {{ shipping.line1 }}
          {{ shipping.line2 ? `, ${shipping.line2}` : "" }}<br />
          {{ shipping.city }}, {{ shipping.state }} {{ shipping.postalCode }},
          {{ shipping.country }}
        </p>
      </v-card>

      <!-- Error -->
      <v-alert
        v-if="submitError"
        type="error"
        variant="tonal"
        rounded="xl"
        class="mb-4"
        closable
        @click:close="submitError = null"
      >
        {{ submitError }}
      </v-alert>

      <div class="d-flex justify-end gap-3">
        <v-btn variant="text" @click="step = 1">Back</v-btn>
        <v-btn
          color="primary"
          variant="flat"
          rounded="xl"
          size="large"
          style="font-weight: 600"
          :loading="submitting"
          @click="placeOrder"
        >
          Place Order · ${{ total }}
        </v-btn>
      </div>
    </template>

    <!-- ────────────────────────────────── STEP 3: Confirmation ──── -->
    <template v-if="step === 3">
      <v-card rounded="xl" border elevation="0" class="pa-10 text-center">
        <v-icon size="72" color="success" class="mb-4"
          >fa:fas fa-circle-check</v-icon
        >
        <h2 class="text-h5 font-weight-bold mb-2" style="color: #1e293b">
          Order Placed!
        </h2>
        <p class="text-body-1 mb-1" style="color: #475569">
          Thank you for your order.
        </p>
        <p class="text-body-2 mb-6" style="color: #64748b">
          Order number:
          <strong style="color: #1e293b">{{
            placedOrder?.order_number
          }}</strong>
          — a confirmation email is on its way.
        </p>
        <div class="d-flex justify-center gap-3">
          <v-btn
            color="primary"
            variant="flat"
            rounded="xl"
            :to="{ name: 'order-detail', params: { id: placedOrder?.id } }"
          >
            View Order
          </v-btn>
          <v-btn variant="text" :to="{ name: 'products' }">Keep Shopping</v-btn>
        </div>
      </v-card>
    </template>
  </v-container>
</template>
