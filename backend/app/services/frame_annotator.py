"""
Frame annotation service using Pillow (no OpenCV).

Draws axis-aligned bounding boxes on video frames.
"""

import io
from PIL import Image, ImageDraw, ImageFont
from app.services.face_detector import Detection


class FrameAnnotator:
    """
    Draws ROI rectangles on frames using Pillow.

    This intentionally avoids OpenCV as required by the assignment.
    """

    BOX_COLOR = (74, 225, 118)   # Green matching frontend --color-secondary
    BOX_WIDTH = 2
    LABEL_BG = (74, 225, 118)
    LABEL_TEXT = (3, 20, 39)     # Dark text on green background

    def annotate(self, frame_bytes: bytes, detection: Detection | None) -> bytes:
        """
        Draw a bounding box on the frame if a face was detected.

        Args:
            frame_bytes: Raw JPEG image bytes.
            detection: Detection result, or None if no face.

        Returns:
            Annotated JPEG image bytes.
        """
        if detection is None:
            return frame_bytes  # Return original frame unmodified

        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(frame_bytes))
            
            # Ensure we can draw on it (needs to be RGB)
            if image.mode != "RGB":
                image = image.convert("RGB")
                
            draw = ImageDraw.Draw(image)
            
            # 1. Draw bounding box
            # Pillow uses [x0, y0, x1, y1] for rectangles
            x0, y0 = detection.x, detection.y
            x1 = x0 + detection.width
            y1 = y0 + detection.height
            
            draw.rectangle(
                [x0, y0, x1, y1],
                outline=self.BOX_COLOR,
                width=self.BOX_WIDTH
            )
            
            # 2. Draw label (Confidence score)
            label = f"{detection.confidence * 100:.1f}%"
            
            # Use default font since we don't have a TTF file guaranteed in the container
            font = ImageFont.load_default()
            
            # Calculate text size to draw background rectangle
            # getbbox returns (left, top, right, bottom)
            text_bbox = font.getbbox(label)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Add padding
            pad_x, pad_y = 4, 2
            
            # Position label above the bounding box, or inside if too close to top
            label_y0 = max(0, y0 - text_height - (pad_y * 2))
            label_y1 = label_y0 + text_height + (pad_y * 2)
            label_x0 = x0
            label_x1 = x0 + text_width + (pad_x * 2)
            
            # Draw label background
            draw.rectangle(
                [label_x0, label_y0, label_x1, label_y1],
                fill=self.LABEL_BG
            )
            
            # Draw text
            draw.text(
                (label_x0 + pad_x, label_y0 + pad_y),
                label,
                fill=self.LABEL_TEXT,
                font=font
            )
            
            # Save annotated image back to bytes
            output = io.BytesIO()
            # Save as JPEG for efficiency since we stream these
            image.save(output, format="JPEG", quality=85)
            return output.getvalue()
            
        except Exception:
            # In case of any error during drawing, fail gracefully
            # by returning the original un-annotated frame
            return frame_bytes
