"""
POST /api/v1/stream/ingest — Accept video frames for processing.
"""

import asyncio
from fastapi import APIRouter, UploadFile, File, status, HTTPException, Request

router = APIRouter(prefix="/api/v1/stream", tags=["stream"])


@router.post(
    "/ingest",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a video frame for face detection",
    description="Accepts a JPEG frame, queues it for face detection processing, "
                "and returns a 202 Accepted. The annotated result will be available via the WebSocket stream.",
    responses={
        202: {"description": "Frame accepted and queued for processing"},
        422: {"description": "Invalid frame data"},
        429: {"description": "Processing queue is full — try again shortly"},
    },
)
async def ingest_frame(
    request: Request,
    frame: UploadFile = File(..., description="JPEG image frame"),
):
    """Accept a single video frame for face detection processing."""
    
    # Validate content type
    if frame.content_type not in ["image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Only JPEG images are supported"
        )
        
    frame_bytes = await frame.read()
    
    # Prevent massive payloads that could OOM the container (e.g., limit to 5MB)
    if len(frame_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Frame size too large (max 5MB)"
        )
        
    # Put frame on the processing queue
    # We use put_nowait to provide backpressure instead of buffering indefinitely
    queue: asyncio.Queue = request.app.state.frame_queue
    try:
        queue.put_nowait(frame_bytes)
    except asyncio.QueueFull:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Processing queue is full — try again shortly"
        )
        
    return {"data": {"queued": True}, "meta": {"status": "accepted"}}
