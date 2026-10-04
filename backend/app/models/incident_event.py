from sqlalchemy import Column, Integer, DateTime
from datetime import datetime, timezone

from app.database import Base


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    event_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )