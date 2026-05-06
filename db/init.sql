-- FaceStream Database Schema
-- PostgreSQL initialization script run on first container startup.

-- Streams table: tracks video streaming sessions
CREATE TABLE IF NOT EXISTS streams (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at    TIMESTAMPTZ,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'ended', 'error')),
    metadata    JSONB DEFAULT '{}'
);

-- ROI Detections: stores each face detection result
CREATE TABLE IF NOT EXISTS roi_detections (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stream_id     UUID NOT NULL REFERENCES streams(id) ON DELETE CASCADE,
    frame_number  BIGINT NOT NULL,

    -- Axis-aligned bounding box (AABB)
    x             INTEGER NOT NULL CHECK (x >= 0),
    y             INTEGER NOT NULL CHECK (y >= 0),
    width         INTEGER NOT NULL CHECK (width > 0),
    height        INTEGER NOT NULL CHECK (height > 0),

    confidence    REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
    detected_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Raw landmark data for potential future use
    landmarks     JSONB
);

-- Performance indexes
-- Most common query: latest detections for a stream
CREATE INDEX IF NOT EXISTS idx_roi_stream_frame
    ON roi_detections (stream_id, frame_number DESC);

-- Time-range queries
CREATE INDEX IF NOT EXISTS idx_roi_detected_at
    ON roi_detections (detected_at DESC);

-- Partial index: only active streams (most queries filter on this)
CREATE INDEX IF NOT EXISTS idx_streams_active
    ON streams (id) WHERE status = 'active';
