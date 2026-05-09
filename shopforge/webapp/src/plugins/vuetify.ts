/**
 * Vuetify plugin configuration.
 *
 * Centralizes theme, defaults, and icon configuration.
 * Icons use Font Awesome Free loaded via CDN in base.html.
 */
import "vuetify/styles";

import { createVuetify } from "vuetify";
import { aliases, fa } from "vuetify/iconsets/fa";

export const vuetify = createVuetify({
  icons: {
    defaultSet: "fa",
    aliases,
    sets: { fa },
  },
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#2563eb",
          secondary: "#64748b",
          success: "#16a34a",
          warning: "#d97706",
          error: "#dc2626",
          info: "#0891b2",
        },
      },
    },
  },
  defaults: {
    VBtn: { variant: "flat", rounded: "lg" },
    VTextField: { variant: "outlined", density: "comfortable" },
    VCard: { rounded: "lg", elevation: 2 },
  },
});
