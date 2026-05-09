<script setup lang="ts">
/** Reusable product card — uses snake_case to match the Django API response. */
export interface Product {
  id: string;
  name: string;
  slug: string;
  short_description: string;
  price: string;
  compare_at_price: string | null;
  category_name: string;
  is_on_sale: boolean;
  discount_percentage: number;
  primary_image: string | null;
}

defineProps<{ product: Product }>();
</script>

<template>
  <v-card
    :to="{ name: 'product-detail', params: { slug: product.slug } }"
    height="100%"
    rounded="xl"
    elevation="0"
    border
    class="product-card"
    style="transition: box-shadow 0.2s, transform 0.2s; overflow: hidden"
  >
    <!-- Image -->
    <div style="position: relative; overflow: hidden">
      <v-img
        :src="product.primary_image ?? ''"
        :alt="product.name"
        height="220"
        cover
        style="background: #F1F5F9"
      >
        <template #placeholder>
          <div class="d-flex align-center justify-center fill-height" style="background: #F1F5F9">
            <v-icon size="48" color="grey-300">fa:far fa-image</v-icon>
          </div>
        </template>
        <template #error>
          <div class="d-flex align-center justify-center fill-height" style="background: #F1F5F9">
            <v-icon size="48" color="grey-300">fa:fas fa-image-slash</v-icon>
          </div>
        </template>
      </v-img>

      <!-- Sale badge -->
      <v-chip
        v-if="product.is_on_sale"
        color="error"
        size="x-small"
        class="font-weight-bold"
        style="position: absolute; top: 10px; right: 10px; letter-spacing: 0.5px"
      >
        -{{ product.discount_percentage }}%
      </v-chip>
    </div>

    <!-- Content -->
    <v-card-text class="pa-4">
      <p class="text-caption text-medium-emphasis mb-1 text-uppercase" style="letter-spacing: 0.8px">
        {{ product.category_name }}
      </p>
      <p
        class="text-body-1 font-weight-semibold mb-1"
        style="color: #1E293B; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden"
      >
        {{ product.name }}
      </p>
      <p
        v-if="product.short_description"
        class="text-body-2 text-medium-emphasis mb-3"
        style="display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden"
      >
        {{ product.short_description }}
      </p>

      <div class="d-flex align-center gap-2">
        <span class="text-h6 font-weight-bold" style="color: #1565C0">${{ product.price }}</span>
        <span
          v-if="product.is_on_sale && product.compare_at_price"
          class="text-body-2 text-decoration-line-through"
          style="color: #94A3B8"
        >
          ${{ product.compare_at_price }}
        </span>
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.product-card:hover {
  box-shadow: 0 8px 24px rgba(21, 101, 192, 0.12) !important;
  transform: translateY(-2px);
}
</style>

