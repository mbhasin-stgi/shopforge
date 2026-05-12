import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";

import { useCartStore } from "../cart";

const ITEM = {
  productId: "uuid-1",
  productName: "Test Product",
  productSlug: "test-product",
  price: "29.99",
  primaryImage: null,
};

describe("Cart Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("starts empty", () => {
    const store = useCartStore();
    expect(store.items).toHaveLength(0);
    expect(store.itemCount).toBe(0);
    expect(store.total).toBe("0.00");
  });

  it("addItem increments itemCount", () => {
    const store = useCartStore();
    store.addItem(ITEM, 2);
    expect(store.itemCount).toBe(2);
    expect(store.items).toHaveLength(1);
  });

  it("addItem accumulates quantity for the same product", () => {
    const store = useCartStore();
    store.addItem(ITEM, 1);
    store.addItem(ITEM, 3);
    expect(store.itemCount).toBe(4);
    expect(store.items).toHaveLength(1);
  });

  it("removeItem removes the correct product", () => {
    const store = useCartStore();
    store.addItem(ITEM, 1);
    store.addItem({ ...ITEM, productId: "uuid-2", productName: "Other" }, 1);
    store.removeItem("uuid-1");
    expect(store.items).toHaveLength(1);
    expect(store.items[0].productId).toBe("uuid-2");
  });

  it("updateQuantity changes item quantity", () => {
    const store = useCartStore();
    store.addItem(ITEM, 1);
    store.updateQuantity("uuid-1", 5);
    expect(store.items[0].quantity).toBe(5);
  });

  it("updateQuantity with 0 removes the item", () => {
    const store = useCartStore();
    store.addItem(ITEM, 1);
    store.updateQuantity("uuid-1", 0);
    expect(store.items).toHaveLength(0);
  });

  it("clearCart empties everything", () => {
    const store = useCartStore();
    store.addItem(ITEM, 3);
    store.clearCart();
    expect(store.items).toHaveLength(0);
    expect(store.itemCount).toBe(0);
  });

  it("total is correct with multiple items", () => {
    const store = useCartStore();
    store.addItem(ITEM, 2); // 29.99 * 2 = 59.98
    store.addItem({ ...ITEM, productId: "uuid-2", price: "10.00" }, 1); // +10.00
    expect(store.total).toBe("69.98");
  });

  it("persists to localStorage on addItem", () => {
    const store = useCartStore();
    store.addItem(ITEM, 1);
    const saved = JSON.parse(localStorage.getItem("cart_items") || "[]");
    expect(saved).toHaveLength(1);
    expect(saved[0].productId).toBe("uuid-1");
  });

  it("loads from localStorage on init", () => {
    localStorage.setItem(
      "cart_items",
      JSON.stringify([{ ...ITEM, quantity: 4 }]),
    );
    setActivePinia(createPinia());
    const store = useCartStore();
    expect(store.itemCount).toBe(4);
  });
});
