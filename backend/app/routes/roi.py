"""
GET /api/v1/roi/latest — Serve ROI detection data from the database.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db
from app.db.models import RoiDetection

router = APIRouter(prefix="/api/v1/roi", tags=["roi"])


@router.get(
    "/latest",
    summary="Get latest face detection results",
    description="Returns the most recent ROI detections with bounding box coordinates, "
                "confidence scores, and timestamps.",
    responses={
        200: {
            "description": "List of recent detections",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "detections": [
                                {
                                    "id": 1,
                                    "stream_id": "123e4567-e89b-12d3-a456-426614174000",
                                    "frame_number": 42,
                                    "x": 120, "y": 80, "width": 200, "height": 250,
                                    "confidence": 0.97,
                                    "detected_at": "2026-05-05T12:00:00Z",
                                }
                            ]
                        },
                        "meta": {"count": 1},
                    }
                }
            },
        }
    },
)
async def get_latest_roi(
    limit: int = Query(default=20, ge=1, le=100, description="Number of detections to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query the latest N face detection results from the database."""
    stmt = select(RoiDetection).order_by(RoiDetection.detected_at.desc()).limit(limit)
    result = await db.execute(stmt)
    detections = result.scalars().all()
    
    # Serialize results manually
    serialized = [
        {
            "id": d.id,
            "stream_id": str(d.stream_id),
            "frame_number": d.frame_number,
            "x": d.x,
            "y": d.y,
            "width": d.width,
            "height": d.height,
            "confidence": d.confidence,
            "detected_at": d.detected_at.isoformat(),
        }
        for d in detections
    ]
    
    return {"data": {"detections": serialized}, "meta": {"count": len(serialized)}}
