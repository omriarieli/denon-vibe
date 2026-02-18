import { appState, wsConnected } from "./stores.js";

let socket = null;
let reconnectTimer = null;

function getWsUrl() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${location.host}/ws`;
}

function handleMessage(event) {
  try {
    const msg = JSON.parse(event.data);

    if (msg.type === "state") {
      // Full state update
      appState.set(msg.data);
    } else {
      // Partial update
      appState.update((s) => ({ ...s, [msg.type]: msg.data }));
    }
  } catch (e) {
    console.error("WS message parse error:", e);
  }
}

export function connectWs() {
  if (socket && socket.readyState <= 1) return;

  socket = new WebSocket(getWsUrl());

  socket.onopen = () => {
    wsConnected.set(true);
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  socket.onmessage = handleMessage;

  socket.onclose = () => {
    wsConnected.set(false);
    scheduleReconnect();
  };

  socket.onerror = () => {
    wsConnected.set(false);
  };
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connectWs();
  }, 3000);
}

export function disconnectWs() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  if (socket) {
    socket.close();
    socket = null;
  }
}
