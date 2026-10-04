from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    message = Column(
        Text,
        nullable=True
    )

    severity = Column(
        String(20),
        nullable=False
    )

    risk_score = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(30),
        default="new",
        nullable=False,
        index=True
    )

    acknowledged_by = Column(
        Integer,
        nullable=True
    )

    resolved_by = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )