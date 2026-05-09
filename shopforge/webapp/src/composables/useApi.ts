/**
 * useApi — generic reactive wrapper around the Axios api instance.
 *
 * Usage:
 *   const { data, loading, error, fetch } = useApi<Product[]>("/products/");
 *   onMounted(fetch);
 */
import { ref } from "vue";
import type { AxiosRequestConfig } from "axios";

import { api } from "@/services/api";

export function useApi<T>(url: string, config?: AxiosRequestConfig) {
  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetch(overrideConfig?: AxiosRequestConfig) {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get<T>(url, { ...config, ...overrideConfig });
      data.value = response.data;
    } catch (err: unknown) {
      if (err instanceof Error) {
        error.value = err.message;
      } else {
        error.value = "An unexpected error occurred.";
      }
    } finally {
      loading.value = false;
    }
  }

  return { data, loading, error, fetch };
}
