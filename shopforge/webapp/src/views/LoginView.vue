<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { useNotification } from "@/composables/useNotification";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const { notify } = useNotification();

const email = ref("");
const password = ref("");
const loading = ref(false);
const showPassword = ref(false);
const errorMessage = ref("");

async function handleLogin() {
  errorMessage.value = "";
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    notify(`Welcome back${auth.fullName ? ", " + auth.fullName : ""}!`, "success");
    const redirect = (route.query.redirect as string) || "/";
    router.push(redirect);
  } catch {
    errorMessage.value = "Invalid email or password. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <v-container fluid class="fill-height pa-0" style="background: #F0F4F8;">
    <v-row no-gutters class="fill-height">

      <!-- Left panel — branding -->
      <v-col
        cols="12"
        md="5"
        class="d-none d-md-flex flex-column justify-center align-center"
        style="background: linear-gradient(145deg, #1565C0 0%, #0D47A1 100%); min-height: 100vh;"
      >
        <div class="text-center px-10">
          <v-icon size="64" color="white" class="mb-6">fa:fas fa-store</v-icon>
          <h1 class="text-h3 font-weight-bold text-white mb-4" style="letter-spacing: -0.5px">
            ShopForge
          </h1>
          <p class="text-h6 text-white" style="opacity: 0.8; font-weight: 400; line-height: 1.6">
            Your corporate e-commerce platform for smart, scalable selling.
          </p>

          <v-divider color="white" class="my-8" style="opacity: 0.2" />

          <div class="d-flex flex-column gap-4 text-white text-left">
            <div v-for="feature in features" :key="feature.text" class="d-flex align-center gap-3">
              <v-icon :icon="feature.icon" size="20" style="opacity: 0.9" />
              <span class="text-body-1" style="opacity: 0.85">{{ feature.text }}</span>
            </div>
          </div>
        </div>
      </v-col>

      <!-- Right panel — form -->
      <v-col cols="12" md="7" class="d-flex align-center justify-center" style="min-height: 100vh">
        <v-card
          flat
          width="100%"
          max-width="440"
          class="pa-8 pa-sm-10 mx-4"
          rounded="xl"
          style="background: white"
        >
          <!-- Header -->
          <div class="mb-8">
            <div class="d-flex align-center gap-2 mb-6 d-md-none">
              <v-icon color="primary" size="24">fa:fas fa-store</v-icon>
              <span class="text-h6 font-weight-bold text-primary">ShopForge</span>
            </div>
            <h2 class="text-h4 font-weight-bold mb-1" style="color: #1E293B; letter-spacing: -0.5px">
              Welcome back
            </h2>
            <p class="text-body-1" style="color: #64748B">Sign in to your account to continue</p>
          </div>

          <!-- Error alert -->
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            rounded="lg"
            closable
            class="mb-6"
            @click:close="errorMessage = ''"
          >
            {{ errorMessage }}
          </v-alert>

          <!-- Form -->
          <v-form @submit.prevent="handleLogin">
            <v-text-field
              v-model="email"
              label="Email address"
              type="email"
              prepend-inner-icon="fa:far fa-envelope"
              autocomplete="email"
              variant="outlined"
              density="comfortable"
              rounded="lg"
              required
              class="mb-3"
              :disabled="loading"
            />

            <v-text-field
              v-model="password"
              label="Password"
              :type="showPassword ? 'text' : 'password'"
              prepend-inner-icon="fa:fas fa-lock"
              :append-inner-icon="showPassword ? 'fa:far fa-eye-slash' : 'fa:far fa-eye'"
              autocomplete="current-password"
              variant="outlined"
              density="comfortable"
              rounded="lg"
              required
              class="mb-6"
              :disabled="loading"
              @click:append-inner="showPassword = !showPassword"
            />

            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              rounded="lg"
              :loading="loading"
              elevation="0"
              style="height: 52px; font-size: 0.95rem; font-weight: 600; letter-spacing: 0.3px"
            >
              Sign In
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
const features = [
  { icon: "fa:fas fa-shield-halved", text: "Enterprise-grade security" },
  { icon: "fa:fas fa-chart-line", text: "Real-time analytics & reporting" },
  { icon: "fa:fas fa-boxes-stacked", text: "Full inventory management" },
];
</script>

