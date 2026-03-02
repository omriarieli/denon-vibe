<script>
  import { sleep } from "../lib/stores.js";
  import { setSleep } from "../lib/api.js";
  import { showToast } from "../lib/toast.js";

  const presets = [0, 15, 30, 60, 90, 120];
  let loading = $state(false);

  async function handlePreset(minutes) {
    loading = true;
    try {
      const res = await setSleep(minutes);
      const val = res.sleep === "OFF" ? "OFF" : `${parseInt(res.sleep, 10)}m`;
      showToast("Sleep", val);
    } catch (e) {
      showToast("Sleep", "Failed", false);
    }
    loading = false;
  }

  function isActive(minutes) {
    if (minutes === 0) return $sleep === "OFF" || $sleep === null;
    return parseInt($sleep, 10) === minutes;
  }
</script>

<div class="sleep-section">
  <div class="sleep-label">Sleep Timer</div>
  <div class="sleep-buttons">
    {#each presets as minutes}
      <button
        class="sleep-btn"
        class:active={isActive(minutes)}
        onclick={() => handlePreset(minutes)}
        disabled={loading}
      >
        {minutes === 0 ? "Off" : `${minutes}m`}
      </button>
    {/each}
  </div>
</div>

<style>
  .sleep-section {
    padding: 12px 16px;
  }
  .sleep-label {
    font-size: 13px;
    color: #888;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .sleep-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .sleep-btn {
    flex: 1;
    min-width: 48px;
    min-height: 48px;
    padding: 10px 4px;
    background: #16213e;
    border: 1px solid #333;
    color: #ccc;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .sleep-btn.active {
    border-color: #e94560;
    color: #e94560;
    background: #2a1a2e;
  }
  .sleep-btn:disabled {
    opacity: 0.5;
  }
</style>
