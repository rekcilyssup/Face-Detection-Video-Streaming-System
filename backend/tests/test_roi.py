"""Tests for GET /api/v1/roi/latest endpoint."""

import pytest

class TestRoiEndpoint:
    """Test suite for the ROI data endpoint."""

    def test_roi_limit_validation_rejects_negative(self, client):
        response = client.get("/api/v1/roi/latest?limit=-5")
        assert response.status_code == 422
        
    def test_roi_limit_validation_rejects_over_100(self, client):
        response = client.get("/api/v1/roi/latest?limit=105")
        assert response.status_code == 422
