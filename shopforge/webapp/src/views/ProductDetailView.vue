<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useNotification } from "@/composables/useNotification";
import { api } from "@/services/api";
import { useCartStore } from "@/stores/cart";

interface ProductImage {
  id: number;
  image: string;
  alt_text: string;
  display_order: number;
  is_primary: boolean;
}

interface ProductDetail {
  id: string;
  name: string;
  slug: string;
  description: string;
  short_description: string;
  price: string;
  compare_at_price: string | null;
  category: { id: number; name: string; slug: string };
  is_on_sale: boolean;
  discount_percentage: number;
  images: ProductImage[];
  in_stock: boolean;
  sku: string;
}

const props = defineProps<{ slug: string }>();

const route = useRoute();
const router = useRouter();
const cart = useCartStore();
const { notify } = useNotification();

const product = ref<ProductDetail | null>(null);
const loading = ref(true);
const quantity = ref(1);
const selectedImage = ref<string | null>(null);

async function fetchProduct() {
  loading.value = true;
  try {
    const slug = props.slug || (route.params.slug as string);
    const response = await api.get(`/products/${slug}/`);
    product.value = response.data;
    const primary = response.data.images?.find(
      (i: ProductImage) => i.is_primary,
    );
    selectedImage.value =
      primary?.image ?? response.data.images?.[0]?.image ?? null;
  } catch {
    router.push({ name: "products" });
  } finally {
    loading.value = false;
  }
}

function addToCart() {
  if (!product.value) return;
  cart.addItem(
    {
      productId: product.value.id,
      productName: product.value.name,
      productSlug: product.value.slug,
      price: product.value.price,
      primaryImage: selectedImage.value,
    },
    quantity.value,
  );
  notify(`${product.value.name} added to cart`, "success");
}

onMounted(fetchProduct);
</script>

<template>
  <v-container class="py-8" style="max-width: 1200px">
    <!-- Loading state -->
    <v-row v-if="loading">
      <v-col cols="12" md="6">
        <v-skeleton-loader type="image" height="460" rounded="xl" />
      </v-col>
      <v-col cols="12" md="6">
        <v-skeleton-loader type="heading" class="mb-4" />
        <v-skeleton-loader type="paragraph" class="mb-4" />
        <v-skeleton-loader type="text" width="40%" class="mb-6" />
        <v-skeleton-loader type="button" width="200px" />
      </v-col>
    </v-row>

    <v-row v-else-if="product">
      <!-- Image column -->
      <v-col cols="12" md="6">
        <!-- Main image -->
        <v-card
          rounded="xl"
          elevation="0"
          border
          class="mb-3 overflow-hidden"
          style="background: #f8fafc"
        >
          <v-img
            :src="selectedImage ?? ''"
            :alt="product.name"
            aspect-ratio="1"
            cover
            style="max-height: 460px"
          >
            <template #placeholder>
              <div class="d-flex align-center justify-center fill-height">
                <v-icon size="64" color="grey-300">fa:far fa-image</v-icon>
              </div>
            </template>
            <template #error>
              <div class="d-flex align-center justify-center fill-height">
                <v-icon size="64" color="grey-300">fa:fas fa-image</v-icon>
              </div>
            </template>
          </v-img>
        </v-card>

        <!-- Thumbnail strip -->
        <div v-if="product.images.length > 1" class="d-flex gap-2 flex-wrap">
          <div
            v-for="img in product.images"
            :key="img.id"
            style="
              width: 72px;
              height: 72px;
              cursor: pointer;
              border-radius: 10px;
              overflow: hidden;
              border: 2px solid transparent;
              transition: border-color 0.15s;
            "
            :style="
              selectedImage === img.image
                ? { borderColor: '#1565C0' }
                : { borderColor: '#E2E8F0' }
            "
            @click="selectedImage = img.image"
          >
            <v-img :src="img.image" cover height="72" />
          </div>
        </div>
      </v-col>

      <!-- Product info column -->
      <v-col cols="12" md="6">
        <!-- Breadcrumb -->
        <v-breadcrumbs
          :items="[
            { title: 'Products', disabled: false, href: '/products' },
            { title: product.category.name, disabled: true },
          ]"
          density="compact"
          class="pa-0 mb-4"
        />

        <!-- Title & badges -->
        <div class="d-flex align-start justify-space-between mb-2">
          <h1
            class="text-h4 font-weight-bold"
            style="color: #1e293b; letter-spacing: -0.5px; line-height: 1.2"
          >
            {{ product.name }}
          </h1>
        </div>

        <p class="text-caption mb-4" style="color: #94a3b8">
          SKU: {{ product.sku }}
        </p>

        <p
          v-if="product.short_description"
          class="text-body-1 mb-4"
          style="color: #475569; line-height: 1.7"
        >
          {{ product.short_description }}
        </p>

        <!-- Price -->
        <div class="d-flex align-center gap-3 mb-4">
          <span class="text-h3 font-weight-black" style="color: #1565c0"
            >${{ product.price }}</span
          >
          <span
            v-if="product.is_on_sale && product.compare_at_price"
            class="text-h6 text-decoration-line-through"
            style="color: #94a3b8"
          >
            ${{ product.compare_at_price }}
          </span>
          <v-chip
            v-if="product.is_on_sale"
            color="error"
            size="small"
            class="font-weight-bold"
          >
            SAVE {{ product.discount_percentage }}%
          </v-chip>
        </div>

        <!-- Stock status -->
        <div class="mb-6">
          <v-chip
            :color="product.in_stock ? 'success' : 'error'"
            variant="tonal"
            :prepend-icon="
              product.in_stock
                ? 'fa:fas fa-circle-check'
                : 'fa:fas fa-circle-xmark'
            "
            size="small"
          >
            {{ product.in_stock ? "In Stock" : "Out of Stock" }}
          </v-chip>
        </div>

        <!-- Add to cart -->
        <v-card rounded="xl" elevation="0" color="grey-50" class="pa-4 mb-6">
          <div class="d-flex align-center gap-4">
            <div class="d-flex align-center border rounded-lg overflow-hidden">
              <v-btn
                icon
                variant="text"
                size="small"
                :disabled="quantity <= 1"
                @click="quantity--"
              >
                <v-icon size="18">fa:fas fa-minus</v-icon>
              </v-btn>
              <span
                class="px-4 text-body-1 font-weight-medium"
                style="min-width: 40px; text-align: center"
              >
                {{ quantity }}
              </span>
              <v-btn
                icon
                variant="text"
                size="small"
                :disabled="quantity >= 99"
                @click="quantity++"
              >
                <v-icon size="18">fa:fas fa-plus</v-icon>
              </v-btn>
            </div>
            <v-btn
              color="primary"
              size="large"
              rounded="xl"
              :disabled="!product.in_stock"
              prepend-icon="fa:fas fa-cart-plus"
              elevation="0"
              style="flex: 1; height: 48px; font-weight: 600"
              @click="addToCart"
            >
              Add to Cart
            </v-btn>
          </div>
        </v-card>

        <!-- Description -->
        <v-divider class="mb-4" />
        <h3 class="text-body-1 font-weight-bold mb-3" style="color: #1e293b">
          Description
        </h3>
        <p
          class="text-body-2"
          style="color: #475569; line-height: 1.8; white-space: pre-line"
        >
          {{ product.description }}
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>
