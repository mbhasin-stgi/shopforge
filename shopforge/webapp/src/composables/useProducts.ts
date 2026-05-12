/**
 * useProducts composable
 *
 * Reusable data-fetching layer for product catalog.
 * Provides loading/error states, filtering, pagination, and debounced search.
 */
import { computed, ref, watch } from "vue";

import type { Product } from "@/components/ProductCard.vue";
import { api } from "@/services/api";

export interface Category {
  id: number;
  name: string;
  slug: string;
  product_count: number;
}

export interface ProductFilters {
  search?: string;
  category?: string;
  min_price?: number | null;
  max_price?: number | null;
  on_sale?: boolean;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface PaginatedProducts {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

export function useProducts(initialFilters: ProductFilters = {}) {
  const products = ref<Product[]>([]);
  const categories = ref<Category[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const totalCount = ref(0);
  const currentPage = ref(initialFilters.page ?? 1);
  const pageSize = ref(initialFilters.page_size ?? 12);
  const hasNext = ref(false);
  const hasPrevious = ref(false);

  const filters = ref<ProductFilters>({ ...initialFilters });

  // Debounce timer for search input
  let _debounceTimer: ReturnType<typeof setTimeout> | null = null;

  const totalPages = computed(
    () => Math.ceil(totalCount.value / pageSize.value) || 1,
  );

  async function fetchProducts(resetPage = false) {
    if (resetPage) {
      currentPage.value = 1;
      filters.value.page = 1;
    }

    loading.value = true;
    error.value = null;

    try {
      const params: Record<string, string | number | boolean> = {
        page: currentPage.value,
        page_size: pageSize.value,
      };
      if (filters.value.search) params.search = filters.value.search;
      if (filters.value.category) params.category = filters.value.category;
      if (filters.value.min_price != null)
        params.min_price = filters.value.min_price;
      if (filters.value.max_price != null)
        params.max_price = filters.value.max_price;
      if (filters.value.on_sale) params.on_sale = true;
      if (filters.value.ordering) params.ordering = filters.value.ordering;

      const response = await api.get<PaginatedProducts>("/products/", {
        params,
      });
      const data = response.data;
      products.value = Array.isArray(data) ? data : data.results;
      totalCount.value = Array.isArray(data) ? data.length : data.count;
      hasNext.value = !Array.isArray(data) && !!data.next;
      hasPrevious.value = !Array.isArray(data) && !!data.previous;
    } catch {
      error.value = "Failed to load products. Please try again.";
    } finally {
      loading.value = false;
    }
  }

  async function fetchCategories() {
    try {
      const response = await api.get<{ results: Category[] } | Category[]>(
        "/products/categories/",
      );
      const data = response.data;
      categories.value = Array.isArray(data) ? data : data.results;
    } catch {
      // Non-critical — silently ignore
    }
  }

  function setSearch(value: string) {
    filters.value.search = value;
    if (_debounceTimer) clearTimeout(_debounceTimer);
    _debounceTimer = setTimeout(() => fetchProducts(true), 300);
  }

  function setCategory(slug: string | null) {
    filters.value.category = slug ?? undefined;
    fetchProducts(true);
  }

  function setPriceRange(min: number | null, max: number | null) {
    filters.value.min_price = min;
    filters.value.max_price = max;
    fetchProducts(true);
  }

  function setOnSale(value: boolean) {
    filters.value.on_sale = value;
    fetchProducts(true);
  }

  function setOrdering(value: string) {
    filters.value.ordering = value;
    fetchProducts(true);
  }

  function goToPage(page: number) {
    currentPage.value = page;
    fetchProducts();
  }

  function nextPage() {
    if (hasNext.value) {
      currentPage.value++;
      fetchProducts();
    }
  }

  function previousPage() {
    if (hasPrevious.value) {
      currentPage.value--;
      fetchProducts();
    }
  }

  // Auto-refetch when filters change (for v-model binding)
  watch(
    () => filters.value.ordering,
    () => fetchProducts(true),
  );

  return {
    products,
    categories,
    loading,
    error,
    totalCount,
    totalPages,
    currentPage,
    pageSize,
    hasNext,
    hasPrevious,
    filters,
    fetchProducts,
    fetchCategories,
    setSearch,
    setCategory,
    setPriceRange,
    setOnSale,
    setOrdering,
    goToPage,
    nextPage,
    previousPage,
  };
}
