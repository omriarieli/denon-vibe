<script>
  import { power } from "../lib/stores.js";
  import { powerOn, powerOff } from "../lib/api.js";

  let loading = $state(false);

  async function toggle() {
    loading = true;
    try {
      if ($power === "ON") {
        await powerOff();
      } else {
        await powerOn();
      }
    } catch (e) {
      console.error("Power toggle failed:", e);
    }
    loading = false;
  }
</script>

<div class="power-section">
  <button
    class="power-btn"
    class:on={$power === "ON"}
    onclick={toggle}
    disabled={loading}
  >
    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 2v10M18.36 6.64A9 9 0 1 1 5.64 6.64" />
    </svg>
    <span>{$power === "ON" ? "ON" : "OFF"}</span>
  </button>
</div>

<style>
  .power-section {
    display: flex;
    justify-content: center;
    padding: 12px 16px;
  }
  .power-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 32px;
    background: #16213e;
    border: 2px solid #333;
    color: #888;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    min-height: 48px;
  }
  .power-btn.on {
    border-color: #4ecca3;
    color: #4ecca3;
    background: #1a2e3e;
  }
  .power-btn:disabled {
    opacity: 0.5;
  }
</style>
