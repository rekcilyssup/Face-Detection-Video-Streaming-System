"""
FaceStream API — Real-time face detection video streaming backend.

FastAPI application entry point.
"""

import os
import uuid
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.routes import ingest, stream, roi
from app.services.face_detector import FaceDetector
from app.services.frame_annotator import FrameAnnotator
from app.db.connection import engine
from app.db.models import Stream, RoiDetection

logger = structlog.get_logger()
settings = get_settings()


async def process_frames_worker(app: FastAPI):
    """Background task to process frames from the queue."""
    logger.info("worker_started")
    detector = FaceDetector(min_confidence=settings.DETECTION_CONFIDENCE)
    annotator = FrameAnnotator()
    
    # Create a single stream session ID for this backend instance's run
    stream_id = uuid.uuid4()
    
    # Initialize the stream record in the DB
    try:
        async with AsyncSession(engine) as session:
            new_stream = Stream(id=stream_id)
            session.add(new_stream)
            await session.commit()
    except Exception as e:
        logger.error("worker_stream_init_failed", error=str(e))
        return

    frame_count = 0
    
    while True:
        try:
            # 1. Get next frame from the queue
            frame_bytes = await app.state.frame_queue.get()
            frame_count += 1
            
            # 2. Detect face
            # Run in a threadpool so we don't block the asyncio event loop
            detection = await asyncio.to_thread(detector.detect, frame_bytes)
            
            # 3. Annotate frame
            annotated_bytes = await asyncio.to_thread(annotator.annotate, frame_bytes, detection)
            
            # 4. Save to database if face was detected
            if detection:
                async with AsyncSession(engine) as session:
                    roi_record = RoiDetection(
                        stream_id=stream_id,
                        frame_number=frame_count,
                        x=detection.x,
                        y=detection.y,
                        width=detection.width,
                        height=detection.height,
                        confidence=detection.confidence,
                        landmarks=detection.landmarks
                    )
                    session.add(roi_record)
                    await session.commit()
            
            # 5. Broadcast annotated frame to all active websockets
            websockets = list(app.state.active_websockets)
            for ws in websockets:
                try:
                    await ws.send_bytes(annotated_bytes)
                except Exception:
                    # Client probably disconnected
                    app.state.active_websockets.discard(ws)
                    
            app.state.frame_queue.task_done()
            
        except asyncio.CancelledError:
            logger.info("worker_cancelled")
            break
        except Exception as e:
            logger.error("worker_error", error=str(e))

    # Clean up
    detector.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("app_starting", app_name=settings.APP_NAME)
    
    # Create queue for frame processing and a set for active WebSockets
    app.state.frame_queue = asyncio.Queue(maxsize=settings.FRAME_QUEUE_SIZE)
    app.state.active_websockets = set()
    
    # Start background worker task
    worker_task = asyncio.create_task(process_frames_worker(app))
    
    yield
    
    # Cancel background worker task on shutdown
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
        
    logger.info("app_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Real-time face detection video streaming API. "
                "Accepts video frames, detects faces using MediaPipe, "
                "draws bounding boxes with Pillow, and streams results via WebSocket.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Routes
app.include_router(ingest.router)
app.include_router(stream.router)
app.include_router(roi.router)


# Health check
@app.get("/api/v1/health", tags=["system"])
async def health_check():
    """Liveness probe for Docker healthcheck."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Global exception handler
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions — returns 500 without leaking internals."""
    logger.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
