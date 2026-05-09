<script setup lang="ts">
import { onMounted, ref } from "vue";

import type { Product } from "@/components/ProductCard.vue";
import ProductCard from "@/components/ProductCard.vue";
import { api } from "@/services/api";

const featured = ref<Product[]>([]);
const loading = ref(true);

async function fetchFeatured() {
  loading.value = true;
  try {
    const response = await api.get("/products/featured/");
    // featured action may return paginated or plain list
    featured.value = response.data.results ?? response.data;
  } catch {
    // Non-critical — page still renders without featured products
  } finally {
    loading.value = false;
  }
}

onMounted(fetchFeatured);
</script>

<template>
  <div>
    <!-- Hero -->
    <div
      style="
        background: linear-gradient(
          135deg,
          #1565c0 0%,
          #0d47a1 60%,
          #01579b 100%
        );
        padding: 80px 24px;
      "
    >
      <v-container style="max-width: 1200px">
        <v-row align="center">
          <v-col cols="12" md="7">
            <p
              class="text-overline font-weight-bold mb-3"
              style="color: rgba(255, 255, 255, 0.7); letter-spacing: 2px"
            >
              Corporate E-Commerce Platform
            </p>
            <h1
              class="font-weight-black mb-4"
              style="
                color: white;
                font-size: clamp(2rem, 4vw, 3.25rem);
                line-height: 1.15;
                letter-spacing: -1px;
              "
            >
              The smarter way to<br />run your store
            </h1>
            <p
              class="text-h6 mb-8"
              style="
                color: rgba(255, 255, 255, 0.8);
                font-weight: 400;
                max-width: 520px;
                line-height: 1.6;
              "
            >
              Discover quality products, manage orders, and grow your business —
              all in one place.
            </p>
            <div class="d-flex gap-3 flex-wrap">
              <v-btn
                :to="{ name: 'products' }"
                color="white"
                variant="flat"
                size="large"
                rounded="xl"
                style="
                  color: #1565c0;
                  font-weight: 700;
                  height: 52px;
                  padding: 0 32px;
                "
              >
                Shop Now
              </v-btn>
              <v-btn
                :to="{ name: 'products' }"
                variant="outlined"
                size="large"
                rounded="xl"
                style="
                  color: white;
                  border-color: rgba(255, 255, 255, 0.5);
                  height: 52px;
                  padding: 0 32px;
                "
              >
                Browse Catalog
              </v-btn>
            </div>
          </v-col>
          <v-col cols="12" md="5" class="d-none d-md-flex justify-center">
            <v-icon size="200" style="color: rgba(255, 255, 255, 0.1)"
              >fa:fas fa-store</v-icon
            >
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Stats bar -->
    <div style="background: white; border-bottom: 1px solid #e2e8f0">
      <v-container style="max-width: 1200px">
        <v-row class="py-6">
          <v-col
            v-for="stat in stats"
            :key="stat.label"
            cols="6"
            sm="3"
            class="text-center"
          >
            <p class="text-h5 font-weight-black mb-1" style="color: #1565c0">
              {{ stat.value }}
            </p>
            <p class="text-body-2" style="color: #64748b">{{ stat.label }}</p>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Featured products -->
    <div style="background: #f8fafc; padding: 64px 24px">
      <v-container style="max-width: 1400px">
        <div class="d-flex align-center justify-space-between mb-6">
          <div>
            <h2 class="text-h5 font-weight-bold mb-1" style="color: #1e293b">
              Featured Products
            </h2>
            <p class="text-body-2" style="color: #64748b">
              Hand-picked selections just for you
            </p>
          </div>
          <v-btn
            :to="{ name: 'products' }"
            variant="tonal"
            color="primary"
            rounded="xl"
            append-icon="fa:fas fa-arrow-right"
          >
            View All
          </v-btn>
        </div>

        <v-row v-if="!loading && featured.length">
          <v-col
            v-for="product in featured"
            :key="product.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <ProductCard :product="product" />
          </v-col>
        </v-row>

        <!-- No featured products -->
        <div
          v-else-if="!loading && !featured.length"
          class="d-flex flex-column align-center py-12"
        >
          <v-icon size="48" color="grey-300" class="mb-3"
            >fa:far fa-star</v-icon
          >
          <p class="text-body-1" style="color: #94a3b8">
            No featured products yet.
          </p>
          <v-btn
            :to="{ name: 'products' }"
            color="primary"
            variant="tonal"
            class="mt-4"
            rounded="xl"
          >
            Browse all products
          </v-btn>
        </div>

        <!-- Loading skeleton -->
        <v-row v-else>
          <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="4" lg="3">
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
    </div>

    <!-- Value propositions -->
    <div style="background: white; padding: 64px 24px">
      <v-container style="max-width: 1200px">
        <h2
          class="text-h5 font-weight-bold text-center mb-2"
          style="color: #1e293b"
        >
          Why ShopForge?
        </h2>
        <p class="text-body-1 text-center mb-10" style="color: #64748b">
          Built for modern commerce at enterprise scale
        </p>
        <v-row>
          <v-col
            v-for="feature in features"
            :key="feature.title"
            cols="12"
            sm="6"
            md="3"
          >
            <div class="text-center pa-4">
              <div
                class="mx-auto mb-4 d-flex align-center justify-center"
                style="
                  width: 56px;
                  height: 56px;
                  background: #eff6ff;
                  border-radius: 16px;
                "
              >
                <v-icon :icon="feature.icon" color="primary" size="26" />
              </div>
              <h3
                class="text-body-1 font-weight-bold mb-2"
                style="color: #1e293b"
              >
                {{ feature.title }}
              </h3>
              <p class="text-body-2" style="color: #64748b; line-height: 1.6">
                {{ feature.desc }}
              </p>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script lang="ts">
const stats = [
  { value: "10K+", label: "Products" },
  { value: "99.9%", label: "Uptime" },
  { value: "50ms", label: "Avg Response" },
  { value: "24/7", label: "Support" },
];

const features = [
  {
    icon: "fa:fas fa-shield-halved",
    title: "Enterprise Security",
    desc: "SOC2 compliant with end-to-end encryption on all transactions.",
  },
  {
    icon: "fa:fas fa-chart-line",
    title: "Real-time Analytics",
    desc: "Live dashboards and reporting to track every sale and trend.",
  },
  {
    icon: "fa:fas fa-boxes-stacked",
    title: "Smart Inventory",
    desc: "Automated reorder alerts and multi-warehouse stock tracking.",
  },
  {
    icon: "fa:fas fa-bolt",
    title: "Blazing Fast",
    desc: "Sub-50ms API responses powered by Redis caching and CDN.",
  },
];
</script>
