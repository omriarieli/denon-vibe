<script>
  import { onMount, onDestroy } from "svelte";
  import { connectWs, disconnectWs } from "./lib/ws.js";
  import ConnectionStatus from "./components/ConnectionStatus.svelte";
  import NowPlaying from "./components/NowPlaying.svelte";
  import VolumeControl from "./components/VolumeControl.svelte";
  import PowerControl from "./components/PowerControl.svelte";
  import SleepTimer from "./components/SleepTimer.svelte";
  import SourceSelect from "./components/SourceSelect.svelte";
  import Favorites from "./components/Favorites.svelte";
  import RadioBrowser from "./components/RadioBrowser.svelte";

  onMount(() => {
    connectWs();
  });

  onDestroy(() => {
    disconnectWs();
  });
</script>

<main>
  <ConnectionStatus />
  <NowPlaying />
  <VolumeControl />
  <div class="row">
    <PowerControl />
    <SourceSelect />
    <SleepTimer />
  </div>
  <Favorites />
  <RadioBrowser />
</main>

<style>
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  :global(body) {
    background: #1a1a2e;
    color: #eee;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    min-height: 100dvh;
  }
  main {
    max-width: 480px;
    margin: 0 auto;
    padding-bottom: 32px;
  }
  .row {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
</style>
