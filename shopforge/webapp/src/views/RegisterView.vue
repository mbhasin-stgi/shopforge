<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const form = ref({
  firstName: "",
  lastName: "",
  email: "",
  password1: "",
  password2: "",
});

const loading = ref(false);
const errorMsg = ref<string | null>(null);
const showPw1 = ref(false);
const showPw2 = ref(false);

const rules = {
  required: (v: string) => !!v || "This field is required.",
  email: (v: string) => /.+@.+\..+/.test(v) || "Enter a valid email address.",
  minLen: (n: number) => (v: string) =>
    v.length >= n || `Minimum ${n} characters.`,
  passwordMatch: () =>
    form.value.password1 === form.value.password2 || "Passwords do not match.",
};

async function submit() {
  errorMsg.value = null;
  if (form.value.password1 !== form.value.password2) {
    errorMsg.value = "Passwords do not match.";
    return;
  }
  loading.value = true;
  try {
    await auth.register(
      form.value.email,
      form.value.password1,
      form.value.password2,
      form.value.firstName,
      form.value.lastName,
    );
    await router.push({ name: "home" });
  } catch (err: unknown) {
    const axiosErr = err as {
      response?: { data?: Record<string, string[]> };
    };
    const data = axiosErr?.response?.data;
    if (data) {
      const messages = Object.values(data).flat().join(" ");
      errorMsg.value = messages || "Registration failed. Please try again.";
    } else {
      errorMsg.value = "Registration failed. Please try again.";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <v-container class="py-12 d-flex justify-center">
    <v-card
      rounded="xl"
      elevation="0"
      border
      style="width: 100%; max-width: 480px"
    >
      <!-- Header -->
      <v-card-text class="pa-8 pb-0">
        <h1
          class="text-h5 font-weight-bold mb-1"
          style="color: #1e293b; letter-spacing: -0.5px"
        >
          Create an account
        </h1>
        <p class="text-body-2" style="color: #64748b">
          Already have one?
          <RouterLink
            :to="{ name: 'login' }"
            style="color: #1565c0; text-decoration: none"
            >Sign in</RouterLink
          >
        </p>
      </v-card-text>

      <v-card-text class="pa-8">
        <!-- Error banner -->
        <v-alert
          v-if="errorMsg"
          type="error"
          variant="tonal"
          rounded="xl"
          class="mb-6"
          closable
          @click:close="errorMsg = null"
        >
          {{ errorMsg }}
        </v-alert>

        <v-form @submit.prevent="submit">
          <!-- Name row -->
          <v-row dense>
            <v-col cols="6">
              <v-text-field
                v-model="form.firstName"
                label="First name"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                :rules="[rules.required]"
                class="mb-1"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.lastName"
                label="Last name"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                :rules="[rules.required]"
                class="mb-1"
              />
            </v-col>
          </v-row>

          <!-- Email -->
          <v-text-field
            v-model="form.email"
            label="Email address"
            type="email"
            autocomplete="email"
            variant="outlined"
            density="comfortable"
            rounded="lg"
            :rules="[rules.required, rules.email]"
            class="mb-2"
          />

          <!-- Password -->
          <v-text-field
            v-model="form.password1"
            :type="showPw1 ? 'text' : 'password'"
            label="Password"
            autocomplete="new-password"
            variant="outlined"
            density="comfortable"
            rounded="lg"
            :rules="[rules.required, rules.minLen(8)]"
            :append-inner-icon="
              showPw1 ? 'fa:fas fa-eye-slash' : 'fa:fas fa-eye'
            "
            class="mb-2"
            @click:append-inner="showPw1 = !showPw1"
          />

          <!-- Confirm password -->
          <v-text-field
            v-model="form.password2"
            :type="showPw2 ? 'text' : 'password'"
            label="Confirm password"
            autocomplete="new-password"
            variant="outlined"
            density="comfortable"
            rounded="lg"
            :rules="[rules.required, rules.passwordMatch]"
            :append-inner-icon="
              showPw2 ? 'fa:fas fa-eye-slash' : 'fa:fas fa-eye'
            "
            class="mb-5"
            @click:append-inner="showPw2 = !showPw2"
          />

          <v-btn
            type="submit"
            color="primary"
            variant="flat"
            rounded="xl"
            block
            size="large"
            style="height: 52px; font-weight: 600"
            :loading="loading"
          >
            Create Account
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>
