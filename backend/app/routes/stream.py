"""
WebSocket /ws/stream — Serve annotated video frames to frontend clients.
"""

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger()

router = APIRouter(tags=["stream"])


@router.websocket("/ws/stream")
async def stream_video(websocket: WebSocket):
    """
    WebSocket endpoint that streams annotated frames to the frontend.

    Frames are JPEG images with bounding boxes drawn by Pillow.
    Sent as binary messages for efficiency.
    """
    await websocket.accept()
    
    # Add client to the set of active websockets
    active_websockets: set = websocket.app.state.active_websockets
    active_websockets.add(websocket)
    
    logger.info("ws_client_connected", client=str(websocket.client))

    try:
        # Keep the connection open and wait for a disconnect
        # The background worker will iterate over `active_websockets` and send frames
        while True:
            # We use receive_text() to detect if the client disconnects or sends a ping
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        logger.info("ws_client_disconnected", client=str(websocket.client))
    except Exception as e:
        logger.error("ws_error", error=str(e), client=str(websocket.client))
    finally:
        # Ensure we remove the client from the active set so the background worker 
        # doesn't try to send to a closed connection
        active_websockets.discard(websocket)
