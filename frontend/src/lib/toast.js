import { writable } from "svelte/store";

let nextId = 0;

export const toasts = writable([]);

export function showToast(label, value, ok = true) {
  const id = ++nextId;
  toasts.update((t) => [...t, { id, label, value, ok }]);
  setTimeout(() => {
    toasts.update((t) => t.filter((x) => x.id !== id));
  }, 2500);
}
