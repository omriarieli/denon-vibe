import { writable, derived } from "svelte/store";

export const appState = writable({
  connected: false,
  avr_ip: null,
  player_id: null,
  power: null,
  volume: null,
  mute: null,
  sleep: null,
  source: null,
  play_state: null,
  now_playing: null,
});

export const wsConnected = writable(false);

export const connected = derived(appState, ($s) => $s.connected);
export const avrIp = derived(appState, ($s) => $s.avr_ip);
export const power = derived(appState, ($s) => $s.power);
export const volume = derived(appState, ($s) => $s.volume);
export const mute = derived(appState, ($s) => $s.mute);
export const sleep = derived(appState, ($s) => $s.sleep);
export const source = derived(appState, ($s) => $s.source);
export const playState = derived(appState, ($s) => $s.play_state);
export const nowPlaying = derived(appState, ($s) => $s.now_playing);
