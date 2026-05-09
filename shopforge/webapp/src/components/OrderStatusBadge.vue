<script setup lang="ts">
/**
 * Colored badge chip for an order's current status.
 */
const STATUS_COLORS: Record<string, string> = {
  pending: "warning",
  confirmed: "info",
  processing: "blue",
  shipped: "purple",
  delivered: "success",
  cancelled: "error",
  refunded: "grey",
};

const props = defineProps<{ status: string }>();

const color = STATUS_COLORS[props.status.toLowerCase()] ?? "default";
</script>

<template>
  <v-chip :color="color" size="small" class="text-uppercase">
    {{ status }}
  </v-chip>
</template>
