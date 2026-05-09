<script setup lang="ts">
/**
 * Global notification snackbar driven by useNotification composable.
 * Include once in App.vue — any component can trigger it via notify().
 */
import { useNotification } from "@/composables/useNotification";

const { state, dismiss } = useNotification();

const ICON: Record<string, string> = {
  success: "fa:fas fa-circle-check",
  error: "fa:fas fa-circle-exclamation",
  warning: "fa:fas fa-triangle-exclamation",
  info: "fa:fas fa-circle-info",
};
</script>

<template>
  <v-snackbar
    v-model="state.visible"
    :timeout="state.timeout"
    :color="state.type"
    location="top right"
    rounded="lg"
    elevation="4"
    min-width="320"
  >
    <div class="d-flex align-center gap-2">
      <v-icon :icon="ICON[state.type]" size="20" />
      <span class="text-body-2 font-weight-medium">{{ state.message }}</span>
    </div>
    <template #actions>
      <v-btn icon size="small" variant="text" @click="dismiss">
        <v-icon size="16">fa:fas fa-xmark</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>
