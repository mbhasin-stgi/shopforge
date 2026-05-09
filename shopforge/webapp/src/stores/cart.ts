/**
 * Cart store — manages shopping cart state.
 *
 * Cart is stored in localStorage so it persists across page reloads.
 */
import { defineStore } from "pinia";
import { computed, ref } from "vue";

interface CartItem {
  productId: string;
  productName: string;
  productSlug: string;
  price: string;
  quantity: number;
  primaryImage: string | null;
}

export const useCartStore = defineStore("cart", () => {
  // ─── State ─────────────────────────────────────────────────────
  const items = ref<CartItem[]>(
    JSON.parse(localStorage.getItem("cart_items") || "[]"),
  );

  // ─── Getters ───────────────────────────────────────────────────
  const itemCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0),
  );

  const total = computed(() =>
    items.value
      .reduce((sum, item) => sum + parseFloat(item.price) * item.quantity, 0)
      .toFixed(2),
  );

  // ─── Actions ───────────────────────────────────────────────────
  function addItem(item: Omit<CartItem, "quantity">, quantity = 1) {
    const existing = items.value.find((i) => i.productId === item.productId);
    if (existing) {
      existing.quantity += quantity;
    } else {
      items.value.push({ ...item, quantity });
    }
    persist();
  }

  function removeItem(productId: string) {
    items.value = items.value.filter((i) => i.productId !== productId);
    persist();
  }

  function updateQuantity(productId: string, quantity: number) {
    const item = items.value.find((i) => i.productId === productId);
    if (item) {
      item.quantity = quantity;
      if (item.quantity <= 0) removeItem(productId);
      else persist();
    }
  }

  function clearCart() {
    items.value = [];
    localStorage.removeItem("cart_items");
  }

  function persist() {
    localStorage.setItem("cart_items", JSON.stringify(items.value));
  }

  return { items, itemCount, total, addItem, removeItem, updateQuantity, clearCart };
});
