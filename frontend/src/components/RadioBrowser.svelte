<script>
  import BrowseItem from "./BrowseItem.svelte";
  import { browseTuneIn, playStation, searchTuneIn } from "../lib/api.js";

  let items = $state([]);
  let loading = $state(false);
  let error = $state(null);
  let breadcrumbs = $state([{ name: "TuneIn", cid: null }]);
  let searchQuery = $state("");
  let searchMode = $state(false);

  async function browse(cid = null) {
    loading = true;
    error = null;
    try {
      items = await browseTuneIn(cid);
    } catch (e) {
      error = e.message;
    }
    loading = false;
  }

  async function handleBrowse(item) {
    await browse(item.cid);
    breadcrumbs = [...breadcrumbs, { name: item.name, cid: item.cid }];
    searchMode = false;
  }

  async function handlePlay(item) {
    try {
      await playStation(item.sid ?? 3, item.cid ?? "", item.mid ?? "", item.name);
    } catch (e) {
      console.error("Play station failed:", e);
    }
  }

  function navigateTo(index) {
    const target = breadcrumbs[index];
    breadcrumbs = breadcrumbs.slice(0, index + 1);
    searchMode = false;
    browse(target.cid);
  }

  async function handleSearch() {
    if (!searchQuery.trim()) return;
    loading = true;
    error = null;
    searchMode = true;
    try {
      items = await searchTuneIn(searchQuery.trim());
    } catch (e) {
      error = e.message;
    }
    loading = false;
  }

  function handleSearchKey(e) {
    if (e.key === "Enter") handleSearch();
  }
</script>

<div class="radio-section">
  <div class="section-header">
    <span class="section-title">Radio</span>
  </div>

  <div class="search-bar">
    <input
      type="text"
      placeholder="Search TuneIn..."
      bind:value={searchQuery}
      onkeydown={handleSearchKey}
      class="search-input"
    />
    <button class="search-btn" onclick={handleSearch} disabled={loading}>Go</button>
  </div>

  <div class="breadcrumbs">
    {#each breadcrumbs as crumb, i}
      {#if i > 0}<span class="sep">/</span>{/if}
      <button class="crumb" onclick={() => navigateTo(i)}>{crumb.name}</button>
    {/each}
    {#if searchMode}
      <span class="sep">/</span>
      <span class="crumb active">Search</span>
    {/if}
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div class="items-list">
    {#if loading}
      <div class="loading">Loading...</div>
    {:else}
      {#each items as item}
        <BrowseItem {item} onplay={handlePlay} onbrowse={handleBrowse} />
      {/each}
      {#if items.length === 0 && !error}
        <div class="empty">
          {breadcrumbs.length === 1 && !searchMode ? "Tap to browse TuneIn" : "No items"}
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .radio-section {
    padding: 0 0 16px;
  }
  .section-header {
    padding: 12px 16px 4px;
  }
  .section-title {
    font-size: 13px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .search-bar {
    display: flex;
    gap: 8px;
    padding: 8px 16px;
  }
  .search-input {
    flex: 1;
    padding: 10px 12px;
    background: #16213e;
    border: 1px solid #333;
    color: #eee;
    border-radius: 8px;
    font-size: 14px;
    min-height: 44px;
  }
  .search-input::placeholder {
    color: #555;
  }
  .search-btn {
    padding: 10px 16px;
    background: #e94560;
    border: none;
    color: #fff;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    min-height: 44px;
  }
  .search-btn:disabled {
    opacity: 0.5;
  }
  .breadcrumbs {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 16px 8px;
    flex-wrap: wrap;
    font-size: 12px;
  }
  .crumb {
    background: none;
    border: none;
    color: #e94560;
    cursor: pointer;
    padding: 2px 4px;
    font-size: 12px;
  }
  .crumb.active {
    color: #888;
    cursor: default;
  }
  .sep {
    color: #444;
  }
  .items-list {
    max-height: 400px;
    overflow-y: auto;
  }
  .error {
    padding: 8px 16px;
    color: #e94560;
    font-size: 13px;
  }
  .loading, .empty {
    padding: 16px;
    color: #555;
    font-size: 13px;
    text-align: center;
  }
</style>
