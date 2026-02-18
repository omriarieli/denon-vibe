<script>
  import { connected, avrIp, wsConnected } from "../lib/stores.js";
  import { rediscover } from "../lib/api.js";

  let discovering = $state(false);

  async function handleRediscover() {
    discovering = true;
    try {
      await rediscover();
    } catch (e) {
      console.error("Rediscover failed:", e);
    }
    discovering = false;
  }
</script>

<div class="connection-bar">
  <span class="status-dot" class:online={$wsConnected && $connected}></span>
  <span class="status-text">
    {#if $connected}
      {$avrIp || "Connected"}
    {:else}
      Disconnected
    {/if}
  </span>
  <button class="rediscover-btn" onclick={handleRediscover} disabled={discovering}>
    {discovering ? "..." : "Reconnect"}
  </button>
</div>

<style>
  .connection-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background: #16213e;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #e94560;
    flex-shrink: 0;
  }
  .status-dot.online {
    background: #4ecca3;
  }
  .status-text {
    flex: 1;
    font-size: 14px;
    color: #ccc;
  }
  .rediscover-btn {
    padding: 6px 12px;
    background: #0f3460;
    border: 1px solid #e94560;
    color: #e94560;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
    min-height: 32px;
  }
  .rediscover-btn:disabled {
    opacity: 0.5;
  }
</style>
