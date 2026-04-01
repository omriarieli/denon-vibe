<script>
  import { onMount } from "svelte";
  import BrowseItem from "./BrowseItem.svelte";
  import { browseFavorites, playPreset } from "../lib/api.js";
  import { showToast } from "../lib/toast.js";

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

  async function handlePlay(preset, item) {
    try {
      await playPreset(preset);
      showToast("Playing", item.name);
    } catch (e) {
      showToast("Favorite", "Failed", false);
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
    {#each items as item, i}
      <BrowseItem {item} onplay={() => handlePlay(i + 1, item)} />
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
