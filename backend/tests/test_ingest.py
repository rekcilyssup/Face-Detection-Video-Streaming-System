"""Tests for POST /api/v1/stream/ingest endpoint."""

import pytest

class TestIngestEndpoint:
    """Test suite for the frame ingest endpoint."""

    def test_ingest_valid_frame_returns_202(self, client, sample_frame: bytes):
        files = {"frame": ("frame.jpg", sample_frame, "image/jpeg")}
        response = client.post("/api/v1/stream/ingest", files=files)
        assert response.status_code == 202
        assert response.json()["data"]["queued"] is True

    def test_ingest_invalid_content_type_returns_422(self, client):
        files = {"frame": ("doc.txt", b"not an image", "text/plain")}
        response = client.post("/api/v1/stream/ingest", files=files)
        assert response.status_code == 422
        assert "Only JPEG" in response.json()["detail"]

    def test_ingest_oversized_frame_rejected(self, client):
        large_file = b"0" * (6 * 1024 * 1024)  # 6MB
        files = {"frame": ("large.jpg", large_file, "image/jpeg")}
        response = client.post("/api/v1/stream/ingest", files=files)
        assert response.status_code == 422
        assert "too large" in response.json()["detail"]
