# FaceStream Frontend

React + TypeScript dashboard for real-time face detection video streaming.

## Features

- **Live webcam capture** — captures frames from the user's camera and sends them to the backend for processing
- **Annotated stream display** — receives processed frames with face detection bounding boxes via WebSocket
- **ROI data panel** — polls the REST API for detection metrics (bounding box coordinates, confidence scores)
- **Detection log** — scrollable history of all face detections with frame numbers and timestamps

## Development

```bash
npm install
npm run dev    # starts on http://localhost:3000
```

The Vite dev server proxies `/api/*` and `/ws/*` to `http://localhost:8000` automatically.

## Production (Docker)

Built as part of the docker-compose stack. See the root `docker-compose.yml`.

```bash
docker build -t facestream-frontend .
```

## Architecture

```
src/
├── config.ts              # API endpoints, polling intervals
├── types.ts               # Shared TypeScript interfaces
├── hooks/
│   ├── useStreamConnection.ts   # WebSocket: receive annotated frames
│   ├── useRoiPolling.ts         # REST: poll /api/v1/roi/latest
│   └── useWebcamIngest.ts       # POST webcam frames to /api/v1/stream/ingest
└── components/
    ├── Header.tsx          # App bar with connection status indicator
    ├── VideoFeed.tsx       # Stream display + start/stop controls
    ├── DetectionPanel.tsx  # ROI metrics + detection log table
    └── Footer.tsx
```
