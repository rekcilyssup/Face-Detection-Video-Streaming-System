"""
SQLAlchemy ORM models for face detection data.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, BigInteger, Integer, String, Float, DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Stream(Base):
    """Represents a video streaming session."""
    __tablename__ = "streams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    metadata_ = Column("metadata", JSONB, default=dict)

    detections = relationship("RoiDetection", back_populates="stream", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'ended', 'error')", name="ck_stream_status"),
        Index("idx_streams_active", "id", postgresql_where="status = 'active'"),
    )


class RoiDetection(Base):
    """Stores a single face detection result (axis-aligned bounding box)."""
    __tablename__ = "roi_detections"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stream_id = Column(UUID(as_uuid=True), ForeignKey("streams.id", ondelete="CASCADE"), nullable=False)
    frame_number = Column(BigInteger, nullable=False)

    # AABB coordinates
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    confidence = Column(Float, nullable=False)
    detected_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    landmarks = Column(JSONB, nullable=True)

    stream = relationship("Stream", back_populates="detections")

    __table_args__ = (
        CheckConstraint("x >= 0", name="ck_roi_x_positive"),
        CheckConstraint("y >= 0", name="ck_roi_y_positive"),
        CheckConstraint("width > 0", name="ck_roi_width_positive"),
        CheckConstraint("height > 0", name="ck_roi_height_positive"),
        CheckConstraint("confidence BETWEEN 0.0 AND 1.0", name="ck_roi_confidence_range"),
        Index("idx_roi_stream_frame", "stream_id", frame_number.desc()),
        Index("idx_roi_detected_at", detected_at.desc()),
    )
