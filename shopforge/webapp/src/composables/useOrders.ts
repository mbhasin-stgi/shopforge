/**
 * useOrders composable
 *
 * Reusable data-fetching and mutation layer for orders.
 */
import { ref } from "vue";

import { api } from "@/services/api";

export interface OrderItem {
  id: string;
  product: string;
  product_name: string;
  product_sku: string;
  price_at_purchase: string;
  quantity: number;
}

export interface Order {
  id: string;
  order_number: string;
  status: string;
  payment_status: string;
  subtotal: string;
  tax_amount: string;
  shipping_cost: string;
  discount_amount: string;
  total: string;
  shipping_address_line1: string;
  shipping_address_line2: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country: string;
  tracking_number: string | null;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface OrderCreatePayload {
  items: { product_id: string; quantity: number }[];
  shipping_address_line1: string;
  shipping_address_line2?: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country?: string;
  coupon_code?: string;
}

export function useOrders() {
  const orders = ref<Order[]>([]);
  const currentOrder = ref<Order | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchOrders() {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get<{ results: Order[] } | Order[]>(
        "/orders/",
      );
      const data = response.data;
      orders.value = Array.isArray(data) ? data : data.results;
    } catch {
      error.value = "Failed to load orders.";
    } finally {
      loading.value = false;
    }
  }

  async function fetchOrder(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get<Order>(`/orders/${id}/`);
      currentOrder.value = response.data;
      return response.data;
    } catch {
      error.value = "Failed to load order details.";
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function cancelOrder(id: string): Promise<Order | null> {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.patch<Order>(`/orders/${id}/cancel/`);
      const index = orders.value.findIndex((o) => o.id === id);
      if (index !== -1) orders.value[index] = response.data;
      if (currentOrder.value?.id === id) currentOrder.value = response.data;
      return response.data;
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: string } } };
      error.value =
        axiosErr?.response?.data?.error ?? "Failed to cancel order.";
      return null;
    } finally {
      loading.value = false;
    }
  }

  return {
    orders,
    currentOrder,
    loading,
    error,
    fetchOrders,
    fetchOrder,
    cancelOrder,
  };
}
