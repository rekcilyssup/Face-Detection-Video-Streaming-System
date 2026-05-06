"""Tests for the FaceDetector service."""

import pytest
from app.services.face_detector import FaceDetector

class TestFaceDetector:
    """Test suite for MediaPipe face detection."""

    def test_detect_returns_none_for_no_face(self, sample_frame):
        """A dummy frame with no face should return None."""
        detector = FaceDetector()
        result = detector.detect(sample_frame)
        assert result is None
        detector.close()

    def test_detector_handles_malformed_jpeg(self):
        """Malformed bytes should be caught gracefully and return None."""
        detector = FaceDetector()
        result = detector.detect(b"this is not a real jpeg")
        assert result is None
        detector.close()
