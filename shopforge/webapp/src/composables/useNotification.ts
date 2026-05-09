/**
 * useNotification — lightweight toast notification system.
 *
 * Backed by a module-level reactive state so any component
 * can trigger a notification without prop-drilling.
 *
 * Usage:
 *   const { notify } = useNotification();
 *   notify("Item added to cart", "success");
 *
 * To display, include <NotificationSnackbar /> in App.vue
 * or listen to { message, type, visible } directly.
 */
import { reactive } from "vue";

type NotificationType = "success" | "error" | "warning" | "info";

const state = reactive({
  visible: false,
  message: "",
  type: "info" as NotificationType,
  timeout: 4000,
});

export function useNotification() {
  function notify(message: string, type: NotificationType = "info", timeout = 4000) {
    state.message = message;
    state.type = type;
    state.timeout = timeout;
    state.visible = true;
  }

  function dismiss() {
    state.visible = false;
  }

  return { state, notify, dismiss };
}
