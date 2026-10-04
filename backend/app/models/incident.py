from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    incident_type = Column(String(100), nullable=False)

    detection_rule = Column(String(100), nullable=True)

    source_ip = Column(String(45), nullable=True, index=True)

    ioc_type = Column(String(30), nullable=True, index=True)

    ioc_value = Column(String(500), nullable=True, index=True)

    event_id = Column(Integer, nullable=True, index=True)

    username = Column(String(100), nullable=True, index=True)

    severity = Column(String(20), default="medium", nullable=False)

    risk_score = Column(Integer, default=0, nullable=False)

    status = Column(String(30), default="open", nullable=False)

    assigned_to = Column(Integer, nullable=True)

    investigation_notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )