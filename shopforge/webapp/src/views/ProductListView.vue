<script setup lang="ts">
import { onMounted, ref } from "vue";

import { api } from "@/services/api";
import ProductCard from "@/components/ProductCard.vue";
import type { Product } from "@/components/ProductCard.vue";

const products = ref<Product[]>([]);
const loading = ref(true);
const search = ref("");
const error = ref(false);

async function fetchProducts() {
  loading.value = true;
  error.value = false;
  try {
    const params: Record<string, string> = {};
    if (search.value) params.search = search.value;
    const response = await api.get("/products/", { params });
    products.value = response.data.results ?? response.data;
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
}

function onClear() {
  search.value = "";
  fetchProducts();
}

onMounted(fetchProducts);
</script>

<template>
  <v-container class="py-8" style="max-width: 1400px">

    <!-- Page header -->
    <div class="mb-6">
      <h1 class="text-h4 font-weight-bold mb-1" style="color: #1E293B; letter-spacing: -0.5px">
        Products
      </h1>
      <p class="text-body-1" style="color: #64748B">
        {{ loading ? "Loading…" : `${products.length} item${products.length !== 1 ? "s" : ""}` }}
      </p>
    </div>

    <!-- Search bar -->
    <v-text-field
      v-model="search"
      placeholder="Search products…"
      prepend-inner-icon="fa:fas fa-magnifying-glass"
      clearable
      variant="outlined"
      density="comfortable"
      rounded="xl"
      hide-details
      class="mb-6"
      style="max-width: 480px"
      @keyup.enter="fetchProducts"
      @click:clear="onClear"
    />

    <!-- Error state -->
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      rounded="xl"
      class="mb-6"
    >
      Failed to load products. Please try again.
      <template #append>
        <v-btn variant="text" @click="fetchProducts">Retry</v-btn>
      </template>
    </v-alert>

    <!-- Product grid -->
    <v-row v-if="!loading && products.length">
      <v-col
        v-for="product in products"
        :key="product.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <ProductCard :product="product" />
      </v-col>
    </v-row>

    <!-- Empty state -->
    <div
      v-else-if="!loading && !products.length && !error"
      class="d-flex flex-column align-center justify-center py-16"
    >
      <v-icon size="64" color="grey-300" class="mb-4">fa:fas fa-box-open</v-icon>
      <h3 class="text-h6 font-weight-medium mb-2" style="color: #475569">No products found</h3>
      <p class="text-body-2" style="color: #94A3B8">
        {{ search ? `No results for "${search}"` : "No products available yet." }}
      </p>
      <v-btn v-if="search" variant="tonal" color="primary" class="mt-4" @click="onClear">
        Clear search
      </v-btn>
    </div>

    <!-- Loading skeleton grid -->
    <v-row v-else-if="loading">
      <v-col v-for="n in 8" :key="n" cols="12" sm="6" md="4" lg="3">
        <v-card rounded="xl" border elevation="0">
          <v-skeleton-loader type="image" height="220" />
          <v-card-text>
            <v-skeleton-loader type="text" class="mb-2" />
            <v-skeleton-loader type="text" width="60%" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

  </v-container>
</template>


