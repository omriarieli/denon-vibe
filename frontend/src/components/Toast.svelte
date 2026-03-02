<script>
  import { toasts } from "../lib/toast.js";
</script>

<div class="toast-container">
  {#each $toasts as t (t.id)}
    <div class="toast" class:error={!t.ok}>
      <span class="toast-label">{t.label}</span>
      <span class="toast-value">{t.value}</span>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: 16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 6px;
    align-items: center;
    pointer-events: none;
  }
  .toast {
    background: #16213e;
    border: 1px solid #4ecca3;
    color: #eee;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    display: flex;
    gap: 8px;
    align-items: center;
    animation: toast-in 0.2s ease-out, toast-out 0.3s ease-in 2.2s forwards;
    white-space: nowrap;
  }
  .toast.error {
    border-color: #e94560;
  }
  .toast-label {
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .toast-value {
    font-weight: 600;
    color: #4ecca3;
  }
  .toast.error .toast-value {
    color: #e94560;
  }
  @keyframes toast-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes toast-out {
    from { opacity: 1; }
    to { opacity: 0; }
  }
</style>
