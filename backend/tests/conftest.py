"""Shared test fixtures."""

import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.db.connection import get_db

@pytest.fixture
def sample_frame() -> bytes:
    """Generate a valid dummy JPEG frame."""
    img = Image.new('RGB', (640, 480), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), "Test Frame", fill=(255,255,0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

@pytest.fixture
def client():
    """Provides a TestClient for testing FastAPI endpoints."""
    from unittest.mock import patch
    import asyncio
    app.dependency_overrides[get_db] = lambda: None
    
    # Patch the background worker so it doesn't crash without DB during tests
    with patch('app.main.process_frames_worker'):
        with TestClient(app) as c:
            c.app.state.frame_queue = asyncio.Queue(maxsize=100)
            c.app.state.active_websockets = set()
            yield c
            
    app.dependency_overrides.clear()
