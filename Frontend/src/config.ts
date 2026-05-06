const API_BASE = import.meta.env.VITE_API_URL || '';

export const config = {
  api: {
    ingest: `${API_BASE}/api/v1/stream/ingest`,
    roi: `${API_BASE}/api/v1/roi/latest`,
    health: `${API_BASE}/api/v1/health`,
  },
  ws: {
    stream: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/stream`,
  },
  polling: {
    roiIntervalMs: 500,
  },
  ingest: {
    frameIntervalMs: 100, // ~10 fps capture rate
  },
};
