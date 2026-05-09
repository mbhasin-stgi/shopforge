<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
import NotificationBar from "@/components/NotificationBar.vue";
</script>

<template>
  <v-app>
    <AppNavbar />
    <v-main>
      <RouterView />
    </v-main>
    <NotificationBar />
  </v-app>
</template>
