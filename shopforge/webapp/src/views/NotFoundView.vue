<script setup lang="ts">
// 404 Not Found view
</script>

<template>
  <v-container class="py-16 d-flex justify-center">
    <div class="text-center" style="max-width: 480px">
      <p
        class="font-weight-black mb-4"
        style="
          font-size: clamp(80px, 20vw, 160px);
          line-height: 1;
          color: #e2e8f0;
          letter-spacing: -4px;
        "
      >
        404
      </p>
      <h1
        class="text-h5 font-weight-bold mb-3"
        style="color: #1e293b; letter-spacing: -0.5px"
      >
        Page not found
      </h1>
      <p class="text-body-1 mb-8" style="color: #64748b">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div class="d-flex justify-center gap-3 flex-wrap">
        <v-btn
          color="primary"
          variant="flat"
          rounded="xl"
          size="large"
          :to="{ name: 'home' }"
        >
          Go Home
        </v-btn>
        <v-btn
          variant="tonal"
          rounded="xl"
          size="large"
          :to="{ name: 'products' }"
        >
          Browse Products
        </v-btn>
      </div>
    </div>
  </v-container>
</template>
