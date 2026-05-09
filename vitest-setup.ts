/**
 * Vitest setup file.
 *
 * Runs before every test file. Sets up global mocks and test utilities.
 */
import { config } from "@vue/test-utils";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

// Create a Vuetify instance for tests
const vuetify = createVuetify({ components, directives });

// Make Vuetify available in all test renders
config.global.plugins = [vuetify];
