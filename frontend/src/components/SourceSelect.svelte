<script>
  import { source } from "../lib/stores.js";
  import { setSource } from "../lib/api.js";
  import { showToast } from "../lib/toast.js";

  const sources = [
    { id: "TV", label: "TV Audio" },
    { id: "SAT/CBL", label: "SAT/CBL" },
    { id: "MPLAY", label: "Media Player" },
    { id: "BD", label: "Blu-ray" },
    { id: "GAME", label: "Game" },
    { id: "AUX1", label: "AUX1" },
    { id: "NET", label: "HEOS" },
    { id: "TUNER", label: "Tuner" },
    { id: "BT", label: "Bluetooth" },
  ];

  let loading = $state(false);

  async function handleSelect(id) {
    if (id === $source) return;
    loading = true;
    try {
      const res = await setSource(id);
      showToast("Source", res.source);
    } catch (e) {
      showToast("Source", "Failed", false);
    }
    loading = false;
  }
</script>

<div class="source-section">
  <div class="source-label">Input Source</div>
  <div class="source-grid">
    {#each sources as s}
      <button
        class="source-btn"
        class:active={$source === s.id}
        onclick={() => handleSelect(s.id)}
        disabled={loading}
      >
        {s.label}
      </button>
    {/each}
  </div>
</div>

<style>
  .source-section {
    padding: 12px 16px;
  }
  .source-label {
    font-size: 13px;
    color: #888;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .source-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  .source-btn {
    padding: 12px 4px;
    background: #16213e;
    border: 1px solid #333;
    color: #ccc;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    min-height: 48px;
    text-align: center;
  }
  .source-btn.active {
    border-color: #e94560;
    color: #e94560;
    background: #2a1a2e;
  }
  .source-btn:disabled {
    opacity: 0.5;
  }
</style>
