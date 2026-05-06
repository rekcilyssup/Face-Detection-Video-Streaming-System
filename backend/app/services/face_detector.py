"""
Face detection service using MediaPipe (no OpenCV).
"""

import io
import numpy as np
from PIL import Image
import mediapipe as mp
from dataclasses import dataclass


@dataclass
class Detection:
    """A single face detection result."""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    landmarks: dict | None = None


class FaceDetector:
    """
    Detects faces in image frames using Google MediaPipe.

    This intentionally avoids OpenCV as required by the assignment.
    Uses Pillow for image decoding and MediaPipe for detection.
    """

    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence
        self._detector = None
        self._mp_face_detection = mp.solutions.face_detection

    def _ensure_detector(self) -> None:
        """Lazy-initialize the MediaPipe detector."""
        if self._detector is None:
            self._detector = self._mp_face_detection.FaceDetection(
                model_selection=0,  # 0 for close range faces
                min_detection_confidence=self.min_confidence
            )

    def detect(self, frame_bytes: bytes) -> Detection | None:
        """
        Detect a face in a raw JPEG frame.

        Args:
            frame_bytes: Raw JPEG image bytes.

        Returns:
            A Detection with AABB coordinates, or None if no face found.
        """
        self._ensure_detector()
        
        try:
            # Decode JPEG using Pillow
            image = Image.open(io.BytesIO(frame_bytes))
            # MediaPipe expects RGB format
            if image.mode != "RGB":
                image = image.convert("RGB")
        except Exception:
            return None
            
        frame_width, frame_height = image.size
        
        # Convert Pillow Image to NumPy array for MediaPipe
        image_np = np.array(image)
        
        # Run detection
        results = self._detector.process(image_np)
        
        if not results.detections:
            return None
            
        # Assignment specifies: "Assume only one face will be present in the video."
        # If multiple are found, we'll take the one with highest confidence
        best_detection = max(results.detections, key=lambda d: d.score[0])
        
        # MediaPipe returns relative bounding box coordinates (0.0 to 1.0)
        bbox = best_detection.location_data.relative_bounding_box
        
        # Convert relative to absolute pixel coordinates
        xmin = int(bbox.xmin * frame_width)
        ymin = int(bbox.ymin * frame_height)
        box_width = int(bbox.width * frame_width)
        box_height = int(bbox.height * frame_height)
        
        # Ensure coordinates are within frame boundaries
        x = max(0, xmin)
        y = max(0, ymin)
        w = min(frame_width - x, box_width)
        h = min(frame_height - y, box_height)
        
        if w <= 0 or h <= 0:
            return None
            
        # Extract landmarks if we need them later
        landmarks_dict = {}
        if hasattr(best_detection.location_data, 'relative_keypoints'):
            landmarks_dict = {
                f"kp_{i}": {"x": kp.x, "y": kp.y}
                for i, kp in enumerate(best_detection.location_data.relative_keypoints)
            }
            
        return Detection(
            x=x,
            y=y,
            width=w,
            height=h,
            confidence=float(best_detection.score[0]),
            landmarks=landmarks_dict
        )

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._detector is not None:
            self._detector.close()
            self._detector = None
