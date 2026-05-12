<script setup lang="ts">
import { onMounted } from "vue";

import ProductCard from "@/components/ProductCard.vue";
import { useProducts } from "@/composables/useProducts";

const {
  products,
  categories,
  loading,
  error,
  totalCount,
  totalPages,
  currentPage,
  filters,
  fetchProducts,
  fetchCategories,
  setSearch,
  setCategory,
  setOnSale,
  setOrdering,
  goToPage,
} = useProducts({ page_size: 12 });

const ORDERING_OPTIONS = [
  { title: "Newest", value: "-created_at" },
  { title: "Price: Low → High", value: "price" },
  { title: "Price: High → Low", value: "-price" },
  { title: "Name A–Z", value: "name" },
];

onMounted(async () => {
  await Promise.all([fetchProducts(), fetchCategories()]);
});
</script>

<template>
  <v-container class="py-8" style="max-width: 1400px">
    <!-- Page header -->
    <div class="mb-6">
      <h1
        class="text-h4 font-weight-bold mb-1"
        style="color: #1e293b; letter-spacing: -0.5px"
      >
        Products
      </h1>
      <p class="text-body-1" style="color: #64748b">
        {{
          loading
            ? "Loading…"
            : `${totalCount} item${totalCount !== 1 ? "s" : ""}`
        }}
      </p>
    </div>

    <v-row>
      <!-- ─── Left sidebar filters ─────────────────────────────── -->
      <v-col cols="12" sm="3">
        <!-- Search -->
        <v-text-field
          :model-value="filters.search ?? ''"
          placeholder="Search products…"
          prepend-inner-icon="fa:fas fa-magnifying-glass"
          clearable
          variant="outlined"
          density="comfortable"
          rounded="xl"
          hide-details
          class="mb-4"
          @update:model-value="(v: string) => setSearch(v)"
          @click:clear="setSearch('')"
        />

        <!-- Category filter -->
        <v-card rounded="xl" border elevation="0" class="mb-4">
          <v-card-text class="pa-4">
            <p
              class="text-caption font-weight-bold text-uppercase mb-3"
              style="color: #64748b"
            >
              Category
            </p>
            <v-chip
              label
              class="mb-2 mr-1"
              :color="!filters.category ? 'primary' : 'default'"
              :variant="!filters.category ? 'flat' : 'tonal'"
              @click="setCategory(null)"
            >
              All
            </v-chip>
            <v-chip
              v-for="cat in categories"
              :key="cat.slug"
              label
              class="mb-2 mr-1"
              :color="filters.category === cat.slug ? 'primary' : 'default'"
              :variant="filters.category === cat.slug ? 'flat' : 'tonal'"
              @click="setCategory(cat.slug)"
            >
              {{ cat.name }}
              <span class="ml-1" style="opacity: 0.6"
                >({{ cat.product_count }})</span
              >
            </v-chip>
          </v-card-text>
        </v-card>

        <!-- On Sale toggle -->
        <v-card rounded="xl" border elevation="0" class="mb-4">
          <v-card-text class="pa-4">
            <v-switch
              :model-value="filters.on_sale ?? false"
              label="On sale only"
              color="primary"
              hide-details
              density="comfortable"
              @update:model-value="(v: boolean) => setOnSale(v)"
            />
          </v-card-text>
        </v-card>

        <!-- Ordering -->
        <v-select
          :model-value="filters.ordering ?? '-created_at'"
          :items="ORDERING_OPTIONS"
          label="Sort by"
          variant="outlined"
          density="comfortable"
          rounded="xl"
          hide-details
          @update:model-value="(v: string) => setOrdering(v)"
        />
      </v-col>

      <!-- ─── Main grid ─────────────────────────────────────────── -->
      <v-col cols="12" sm="9">
        <!-- Error state -->
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          rounded="xl"
          class="mb-6"
        >
          {{ error }}
          <template #append>
            <v-btn variant="text" @click="fetchProducts()">Retry</v-btn>
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
          >
            <ProductCard :product="product" />
          </v-col>
        </v-row>

        <!-- Empty state -->
        <div
          v-else-if="!loading && !products.length && !error"
          class="d-flex flex-column align-center justify-center py-16"
        >
          <v-icon size="64" color="grey-300" class="mb-4"
            >fa:fas fa-box-open</v-icon
          >
          <h3 class="text-h6 font-weight-medium mb-2" style="color: #475569">
            No products found
          </h3>
          <p class="text-body-2" style="color: #94a3b8">
            {{
              filters.search
                ? `No results for "${filters.search}"`
                : "No products available yet."
            }}
          </p>
          <v-btn
            v-if="filters.search || filters.category"
            variant="tonal"
            color="primary"
            class="mt-4"
            @click="
              () => {
                setSearch('');
                setCategory(null);
              }
            "
          >
            Clear filters
          </v-btn>
        </div>

        <!-- Loading skeleton grid -->
        <v-row v-else-if="loading">
          <v-col v-for="n in 9" :key="n" cols="12" sm="6" md="4">
            <v-card rounded="xl" border elevation="0">
              <v-skeleton-loader type="image" height="220" />
              <v-card-text>
                <v-skeleton-loader type="text" class="mb-2" />
                <v-skeleton-loader type="text" width="60%" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Pagination -->
        <div
          v-if="totalPages > 1 && !loading"
          class="d-flex justify-center mt-8"
        >
          <v-pagination
            :model-value="currentPage"
            :length="totalPages"
            :total-visible="7"
            rounded="xl"
            @update:model-value="(p: number) => goToPage(p)"
          />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>
