<script>
  let { item, onplay, onbrowse } = $props();

  function handleClick() {
    if (item.container && onbrowse) {
      onbrowse(item);
    } else if (item.playable && onplay) {
      onplay(item);
    }
  }
</script>

<button class="browse-item" onclick={handleClick} class:playable={item.playable}>
  {#if item.image_url}
    <img class="item-img" src={item.image_url} alt="" />
  {:else}
    <div class="item-img placeholder">
      {#if item.container}
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
        </svg>
      {:else}
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" /><polygon points="10,8 16,12 10,16" fill="currentColor" />
        </svg>
      {/if}
    </div>
  {/if}
  <span class="item-name">{item.name}</span>
  {#if item.container}
    <svg class="chevron" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  {/if}
</button>

<style>
  .browse-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    background: none;
    border: none;
    border-bottom: 1px solid #222;
    color: #ccc;
    font-size: 14px;
    text-align: left;
    cursor: pointer;
    min-height: 48px;
  }
  .browse-item:active {
    background: #16213e;
  }
  .item-img {
    width: 40px;
    height: 40px;
    border-radius: 6px;
    object-fit: cover;
    flex-shrink: 0;
  }
  .item-img.placeholder {
    background: #16213e;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #555;
  }
  .item-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .chevron {
    color: #555;
    flex-shrink: 0;
  }
</style>
