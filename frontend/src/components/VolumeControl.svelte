<script>
  import { volume, mute } from "../lib/stores.js";
  import { setVolume, volumeUp, volumeDown, toggleMute } from "../lib/api.js";

  let debounceTimer = null;
  let localVolume = $state(null);
  let dragging = $state(false);

  // Sync local volume from store when not dragging
  $effect(() => {
    if (!dragging && $volume !== null) {
      localVolume = $volume;
    }
  });

  function handleInput(e) {
    const val = parseInt(e.target.value);
    localVolume = val;
    dragging = true;
    // Debounce during drag
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      setVolume(val).catch(console.error);
    }, 150);
  }

  function handleChange(e) {
    dragging = false;
    clearTimeout(debounceTimer);
    const val = parseInt(e.target.value);
    localVolume = val;
    setVolume(val).catch(console.error);
  }

  function handleMute() {
    toggleMute().catch(console.error);
  }

  function handleUp() {
    volumeUp().catch(console.error);
  }

  function handleDown() {
    volumeDown().catch(console.error);
  }

  let displayVolume = $derived(localVolume !== null ? localVolume : ($volume ?? 0));
</script>

<div class="volume-section">
  <div class="volume-header">
    <button class="mute-btn" class:muted={$mute === "ON"} onclick={handleMute}>
      {#if $mute === "ON"}
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 5L6 9H2v6h4l5 4V5z" /><line x1="23" y1="9" x2="17" y2="15" /><line x1="17" y1="9" x2="23" y2="15" />
        </svg>
      {:else}
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 5L6 9H2v6h4l5 4V5z" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
        </svg>
      {/if}
    </button>
    <span class="volume-value">{displayVolume}</span>
  </div>
  <div class="slider-row">
    <button class="vol-btn" onclick={handleDown}>-</button>
    <input
      type="range"
      min="0"
      max="98"
      value={displayVolume}
      oninput={handleInput}
      onchange={handleChange}
      class="volume-slider"
    />
    <button class="vol-btn" onclick={handleUp}>+</button>
  </div>
</div>

<style>
  .volume-section {
    padding: 12px 16px;
  }
  .volume-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }
  .mute-btn {
    background: none;
    border: none;
    color: #ccc;
    cursor: pointer;
    padding: 8px;
    border-radius: 8px;
    min-width: 48px;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .mute-btn.muted {
    color: #e94560;
  }
  .volume-value {
    font-size: 28px;
    font-weight: 700;
    color: #eee;
    font-variant-numeric: tabular-nums;
  }
  .slider-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .vol-btn {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #16213e;
    border: 1px solid #333;
    color: #ccc;
    font-size: 22px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .volume-slider {
    flex: 1;
    height: 8px;
    -webkit-appearance: none;
    appearance: none;
    background: #333;
    border-radius: 4px;
    outline: none;
  }
  .volume-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #e94560;
    cursor: pointer;
  }
  .volume-slider::-moz-range-thumb {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #e94560;
    cursor: pointer;
    border: none;
  }
</style>
