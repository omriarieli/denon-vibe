const BASE = "/api";

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: {},
  };
  if (body !== null) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// System
export const getStatus = () => request("GET", "/status");
export const rediscover = () => request("POST", "/discover");

// AVR
export const getPower = () => request("GET", "/avr/power");
export const powerOn = () => request("POST", "/avr/power/on");
export const powerOff = () => request("POST", "/avr/power/off");
export const getVolume = () => request("GET", "/avr/volume");
export const setVolume = (level) => request("POST", "/avr/volume", { level });
export const volumeUp = () => request("POST", "/avr/volume/up");
export const volumeDown = () => request("POST", "/avr/volume/down");
export const toggleMute = () => request("POST", "/avr/mute/toggle");
export const getSleep = () => request("GET", "/avr/sleep");
export const setSleep = (minutes) =>
  request("POST", "/avr/sleep", { minutes });
export const getSource = () => request("GET", "/avr/source");
export const setSource = (source) =>
  request("POST", "/avr/source", { source });

// HEOS
export const getNowPlaying = () => request("GET", "/heos/now-playing");
export const setPlayState = (state) =>
  request("POST", "/heos/play-state", { state });
export const browseTuneIn = (cid = null) =>
  request("GET", cid ? `/heos/browse/tunein/${cid}` : "/heos/browse/tunein");
export const playStation = (sid, cid, mid, name) =>
  request("POST", "/heos/play/station", { sid, cid, mid, name });
export const browseFavorites = () => request("GET", "/heos/browse/favorites");
export const playPreset = (preset) =>
  request("POST", "/heos/play/preset", { preset });
export const searchTuneIn = (q) =>
  request("GET", `/heos/search/tunein?q=${encodeURIComponent(q)}`);
