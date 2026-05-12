<script setup lang="ts">
import { onMounted, ref } from "vue";

import { api } from "@/services/api";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

// ─── Profile form ─────────────────────────────────────────────────
const profile = ref({
  first_name: "",
  last_name: "",
  email: "",
  phone_number: "",
});
const profileLoading = ref(false);
const profileSuccess = ref(false);
const profileError = ref<string | null>(null);

// ─── Password change form ─────────────────────────────────────────
const pw = ref({ old_password: "", new_password1: "", new_password2: "" });
const pwLoading = ref(false);
const pwSuccess = ref(false);
const pwError = ref<string | null>(null);
const showOldPw = ref(false);
const showNewPw = ref(false);

onMounted(async () => {
  await auth.fetchProfile();
  if (auth.user) {
    profile.value.first_name = auth.user.first_name;
    profile.value.last_name = auth.user.last_name;
    profile.value.email = auth.user.email;
    profile.value.phone_number = auth.user.phone_number ?? "";
  }
});

async function saveProfile() {
  profileLoading.value = true;
  profileError.value = null;
  profileSuccess.value = false;
  try {
    await auth.updateProfile({
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      phone_number: profile.value.phone_number,
    });
    profileSuccess.value = true;
    setTimeout(() => (profileSuccess.value = false), 3000);
  } catch {
    profileError.value = "Failed to update profile.";
  } finally {
    profileLoading.value = false;
  }
}

async function changePassword() {
  pwLoading.value = true;
  pwError.value = null;
  pwSuccess.value = false;
  if (pw.value.new_password1 !== pw.value.new_password2) {
    pwError.value = "New passwords do not match.";
    pwLoading.value = false;
    return;
  }
  try {
    await api.post("/auth/password/change/", pw.value);
    pw.value = { old_password: "", new_password1: "", new_password2: "" };
    pwSuccess.value = true;
    setTimeout(() => (pwSuccess.value = false), 3000);
  } catch (err: unknown) {
    const axiosErr = err as {
      response?: { data?: Record<string, string[]> };
    };
    const data = axiosErr?.response?.data;
    if (data) {
      pwError.value = Object.values(data).flat().join(" ");
    } else {
      pwError.value = "Failed to change password.";
    }
  } finally {
    pwLoading.value = false;
  }
}
</script>

<template>
  <v-container class="py-8" style="max-width: 640px">
    <h1
      class="text-h4 font-weight-bold mb-8"
      style="color: #1e293b; letter-spacing: -0.5px"
    >
      My Profile
    </h1>

    <!-- Profile card -->
    <v-card rounded="xl" border elevation="0" class="pa-6 mb-6">
      <h2 class="text-subtitle-1 font-weight-bold mb-5" style="color: #1e293b">
        Personal Information
      </h2>

      <v-alert
        v-if="profileSuccess"
        type="success"
        variant="tonal"
        rounded="lg"
        density="compact"
        class="mb-4"
      >
        Profile updated successfully.
      </v-alert>
      <v-alert
        v-if="profileError"
        type="error"
        variant="tonal"
        rounded="lg"
        density="compact"
        class="mb-4"
        closable
        @click:close="profileError = null"
      >
        {{ profileError }}
      </v-alert>

      <v-row>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="profile.first_name"
            label="First name"
            variant="outlined"
            density="comfortable"
            rounded="lg"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="profile.last_name"
            label="Last name"
            variant="outlined"
            density="comfortable"
            rounded="lg"
          />
        </v-col>
      </v-row>
      <v-text-field
        v-model="profile.email"
        label="Email address"
        variant="outlined"
        density="comfortable"
        rounded="lg"
        readonly
        class="mb-2"
        hint="Email cannot be changed."
        persistent-hint
      />
      <v-text-field
        v-model="profile.phone_number"
        label="Phone number"
        variant="outlined"
        density="comfortable"
        rounded="lg"
        class="mb-4"
      />
      <v-btn
        color="primary"
        variant="flat"
        rounded="xl"
        :loading="profileLoading"
        @click="saveProfile"
      >
        Save Changes
      </v-btn>
    </v-card>

    <!-- Password card -->
    <v-card rounded="xl" border elevation="0" class="pa-6">
      <h2 class="text-subtitle-1 font-weight-bold mb-5" style="color: #1e293b">
        Change Password
      </h2>

      <v-alert
        v-if="pwSuccess"
        type="success"
        variant="tonal"
        rounded="lg"
        density="compact"
        class="mb-4"
      >
        Password changed successfully.
      </v-alert>
      <v-alert
        v-if="pwError"
        type="error"
        variant="tonal"
        rounded="lg"
        density="compact"
        class="mb-4"
        closable
        @click:close="pwError = null"
      >
        {{ pwError }}
      </v-alert>

      <v-text-field
        v-model="pw.old_password"
        :type="showOldPw ? 'text' : 'password'"
        label="Current password"
        variant="outlined"
        density="comfortable"
        rounded="lg"
        :append-inner-icon="showOldPw ? 'fa:fas fa-eye-slash' : 'fa:fas fa-eye'"
        class="mb-3"
        @click:append-inner="showOldPw = !showOldPw"
      />
      <v-text-field
        v-model="pw.new_password1"
        :type="showNewPw ? 'text' : 'password'"
        label="New password"
        variant="outlined"
        density="comfortable"
        rounded="lg"
        :append-inner-icon="showNewPw ? 'fa:fas fa-eye-slash' : 'fa:fas fa-eye'"
        class="mb-3"
        @click:append-inner="showNewPw = !showNewPw"
      />
      <v-text-field
        v-model="pw.new_password2"
        :type="showNewPw ? 'text' : 'password'"
        label="Confirm new password"
        variant="outlined"
        density="comfortable"
        rounded="lg"
        class="mb-4"
      />
      <v-btn
        color="primary"
        variant="flat"
        rounded="xl"
        :loading="pwLoading"
        @click="changePassword"
      >
        Change Password
      </v-btn>
    </v-card>
  </v-container>
</template>
