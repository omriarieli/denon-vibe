<script>
  import { nowPlaying, playState } from "../lib/stores.js";
  import { setPlayState } from "../lib/api.js";
  import { showToast } from "../lib/toast.js";

  let loading = $state(false);

  async function handlePlayState(state) {
    loading = true;
    try {
      const res = await setPlayState(state);
      showToast("Playback", res.state);
    } catch (e) {
      showToast("Playback", "Failed", false);
    }
    loading = false;
  }
</script>

<div class="now-playing">
  {#if $nowPlaying?.image_url}
    <img class="album-art" src={$nowPlaying.image_url} alt="Album art" />
  {:else}
    <div class="album-art placeholder">
      <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3" />
      </svg>
    </div>
  {/if}

  <div class="track-info">
    {#if $nowPlaying?.station}
      <div class="station">{$nowPlaying.station}</div>
    {/if}
    {#if $nowPlaying?.song}
      <div class="song">{$nowPlaying.song}</div>
    {/if}
    {#if $nowPlaying?.artist}
      <div class="artist">{$nowPlaying.artist}</div>
    {/if}
    {#if $nowPlaying?.album}
      <div class="album">{$nowPlaying.album}</div>
    {/if}
    {#if !$nowPlaying?.song && !$nowPlaying?.station}
      <div class="no-track">Nothing playing</div>
    {/if}
  </div>

  <div class="controls">
    <button class="ctrl-btn" onclick={() => handlePlayState("stop")} disabled={loading} aria-label="Stop">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="1" /></svg>
    </button>
    {#if $playState === "play"}
      <button class="ctrl-btn primary" onclick={() => handlePlayState("pause")} disabled={loading} aria-label="Pause">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1" /><rect x="14" y="4" width="4" height="16" rx="1" /></svg>
      </button>
    {:else}
      <button class="ctrl-btn primary" onclick={() => handlePlayState("play")} disabled={loading} aria-label="Play">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor"><polygon points="6,4 20,12 6,20" /></svg>
      </button>
    {/if}
  </div>
</div>

<style>
  .now-playing {
    padding: 16px;
    text-align: center;
  }
  .album-art {
    width: 160px;
    height: 160px;
    border-radius: 12px;
    object-fit: cover;
    margin: 0 auto 12px;
    display: block;
  }
  .album-art.placeholder {
    background: #16213e;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #444;
  }
  .track-info {
    margin-bottom: 12px;
  }
  .station {
    font-size: 11px;
    color: #e94560;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }
  .song {
    font-size: 18px;
    font-weight: 600;
    color: #eee;
    margin-bottom: 2px;
  }
  .artist {
    font-size: 14px;
    color: #aaa;
  }
  .album {
    font-size: 12px;
    color: #666;
    margin-top: 2px;
  }
  .no-track {
    font-size: 14px;
    color: #555;
  }
  .controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
  }
  .ctrl-btn {
    background: #16213e;
    border: 1px solid #333;
    color: #ccc;
    border-radius: 50%;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
  }
  .ctrl-btn.primary {
    width: 56px;
    height: 56px;
    border-color: #e94560;
    color: #e94560;
  }
  .ctrl-btn:disabled {
    opacity: 0.5;
  }
</style>
