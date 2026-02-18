<script>
  import { onMount } from "svelte";
  import BrowseItem from "./BrowseItem.svelte";
  import { browseFavorites, playPreset } from "../lib/api.js";

  let items = $state([]);
  let loading = $state(false);
  let error = $state(null);

  onMount(loadFavorites);

  async function loadFavorites() {
    loading = true;
    error = null;
    try {
      items = await browseFavorites();
    } catch (e) {
      error = e.message;
    }
    loading = false;
  }

  async function handlePlay(item) {
    // Favorites are played by preset index (1-based)
    const idx = items.indexOf(item) + 1;
    try {
      await playPreset(idx);
    } catch (e) {
      console.error("Play preset failed:", e);
    }
  }
</script>

<div class="favorites-section">
  <div class="section-header">
    <span class="section-title">Favorites</span>
    <button class="refresh-btn" onclick={loadFavorites} disabled={loading}>
      {loading ? "..." : "Refresh"}
    </button>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div class="items-list">
    {#each items as item}
      <BrowseItem {item} onplay={handlePlay} />
    {/each}
    {#if !loading && items.length === 0 && !error}
      <div class="empty">No favorites found</div>
    {/if}
  </div>
</div>

<style>
  .favorites-section {
    padding: 0 0 8px;
  }
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px 4px;
  }
  .section-title {
    font-size: 13px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .refresh-btn {
    background: none;
    border: none;
    color: #e94560;
    font-size: 12px;
    cursor: pointer;
    padding: 4px 8px;
  }
  .items-list {
    max-height: 300px;
    overflow-y: auto;
  }
  .error {
    padding: 8px 16px;
    color: #e94560;
    font-size: 13px;
  }
  .empty {
    padding: 16px;
    color: #555;
    font-size: 13px;
    text-align: center;
  }
</style>
