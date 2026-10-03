from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(String(50), nullable=False, index=True)

    source_ip = Column(String(45), nullable=True, index=True)

    username = Column(String(100), nullable=True, index=True)

    action = Column(String(100), nullable=True)

    status = Column(String(30), nullable=True)

    severity = Column(String(20), default="low", nullable=False)

    message = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )